from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import InvoiceSerializer
from django.template.loader import render_to_string
from django.http import HttpResponse
import pdfkit
import logging
from rest_framework import status
from django.conf import settings
import os
import re

# Configure logging
logger = logging.getLogger(__name__)

class BillGen(APIView):
    def post(self, request):
        serializer = InvoiceSerializer(data=request.data)
        try:
            # Validate serializer
            if not serializer.is_valid():
                logger.warning(f"Invoice validation failed: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            # Get validated data
            context = serializer.validated_data
            
            total_net_wt = sum(item['net_wt'] for item in context["product_items"])
            html_string = render_to_string('invoice.html', {'user': context,"total_net_wt": total_net_wt})
            
            # PDF generation options
            options = {
                'page-size': 'A4',
                'encoding': 'UTF-8',
                'margin-top': '10mm',
                'margin-right': '10mm',
                'margin-bottom': '10mm',
                'margin-left': '10mm',
            }

            # Optional: Custom wkhtmltopdf path
            wkhtmltopdf_path = getattr(settings, 'WKHTMLTOPDF_PATH', None)
            
            try:
                # Generate PDF
                if wkhtmltopdf_path and os.path.exists(wkhtmltopdf_path):
                    config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
                    pdf_content = pdfkit.from_string(html_string, False, options=options, configuration=config)
                else:
                    pdf_content = pdfkit.from_string(html_string, False, options=options)
            
            except OSError as e:
                logger.error(f"wkhtmltopdf error: {str(e)}")
                return Response(
                    {'error': 'PDF generation tool is not installed or accessible'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Generate dynamic filename
            bill_no = context.get('bill_no', 'invoice')
            cust_name = context.get('cust_name', 'customer')
            
            # Sanitize filename
            bill_no = re.sub(r'[^\w\-_\.]', '_', bill_no)
            cust_name = re.sub(r'[^\w\-_\.]', '_', cust_name)
            
            filename = f"{bill_no}_{cust_name}_invoice.pdf"
            
            # Create response
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
        
        except Exception as e:
            # Catch and log any unexpected errors
            logger.error(f"Invoice generation error: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Failed to generate invoice', 'details': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )