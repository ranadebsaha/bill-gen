from rest_framework import serializers

class ProductItemSerializer(serializers.Serializer):
    si_no = serializers.CharField(required=False, allow_blank=True)
    des = serializers.CharField(max_length=255)
    hsn_code = serializers.CharField(max_length=50, required=False, allow_blank=True)
    pc = serializers.CharField(required=False, allow_blank=True)
    purity = serializers.CharField(max_length=50, required=False, allow_blank=True)
    net_wt = serializers.FloatField()
    gold_value = serializers.CharField(max_length=50)
    making_charges = serializers.CharField(max_length=50)
    amount = serializers.CharField(max_length=50)

    def validate_amount(self, value):
        try:
            float(value)
            return value
        except ValueError:
            raise serializers.ValidationError("Amount must be a valid number")

class ReceiptSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    value = serializers.CharField(max_length=50)

class TermsConditionSerializer(serializers.Serializer):
    def to_internal_value(self, data):
        if isinstance(data, dict):
            return list(data.values())
        elif isinstance(data, list):
            return data
        else:
            raise serializers.ValidationError("Terms and conditions must be a dictionary or list")

class InvoiceSerializer(serializers.Serializer):
    # Shop Details
    id = serializers.CharField(required=False, allow_blank=True)
    shop_name = serializers.CharField(max_length=255)
    estd = serializers.CharField(max_length=50, required=False, allow_blank=True)
    phone_no_1 = serializers.CharField(max_length=20)
    phone_no_2 = serializers.CharField(max_length=20, required=False, allow_blank=True)
    email = serializers.EmailField()
    address = serializers.CharField(max_length=500)
    gst = serializers.CharField(max_length=50)
    hallmark = serializers.CharField(max_length=50, required=False, allow_blank=True)

    # Invoice Details
    bill_no = serializers.CharField(max_length=50)
    date = serializers.CharField(max_length=50)
    item_type = serializers.CharField(max_length=100)
    purity = serializers.CharField(max_length=50)
    rate_per_gm = serializers.CharField(max_length=50)
    sm_code = serializers.CharField(max_length=50, required=False, allow_blank=True)

    # Customer Details
    cust_name = serializers.CharField(max_length=255)
    cust_address = serializers.CharField(max_length=500)
    cust_phone = serializers.CharField(max_length=20)
    cust_state = serializers.CharField(max_length=100)
    cust_pin = serializers.CharField(max_length=20)

    # Product Items
    product_items = ProductItemSerializer(many=True)

    # Financial Details
    total_amount = serializers.CharField(max_length=50)
    sgst_persent = serializers.CharField(max_length=10)
    cgst_persent = serializers.CharField(max_length=10)
    sgst = serializers.CharField(max_length=50)
    cgst = serializers.CharField(max_length=50)
    total_amount_with_tax = serializers.CharField(max_length=50)
    round_off = serializers.CharField(max_length=50, required=False, allow_blank=True)
    
    # Receipts
    receipts = ReceiptSerializer(many=True, required=False)
    
    # Balance Details
    balance_amount = serializers.CharField(max_length=50)
    balance_amount_in_words = serializers.CharField(max_length=500)

    # Other Details
    t_c = TermsConditionSerializer(required=False)
    bank_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    ac_no = serializers.CharField(max_length=50, required=False, allow_blank=True)
    ifsc = serializers.CharField(max_length=20, required=False, allow_blank=True)
    note = serializers.CharField(max_length=500, required=False, allow_blank=True)
    tagline_1 = serializers.CharField(max_length=255, required=False, allow_blank=True)
    tagline_2 = serializers.CharField(max_length=255, required=False, allow_blank=True)

    def validate(self, data):
        if 'product_items' in data:
            calculated_total = sum(
                float(item['amount'].replace(',', '')) 
                for item in data['product_items']
            )
            invoice_total = float(data['total_amount'].replace(',', ''))
            
            # Allow small discrepancies (e.g., rounding)
            if abs(calculated_total - invoice_total) > 0.5:
                raise serializers.ValidationError({
                    'total_amount': 'Total amount does not match sum of product items'
                })
        
        return data

    def to_internal_value(self, data):
        if 'receipt_name' in data and 'receipt_value' in data:
            data['receipts'] = [
                {'name': name, 'value': value} 
                for name, value in zip(data.get('receipt_name', []), data.get('receipt_value', []))
            ]
        
        return super().to_internal_value(data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if 'receipts' in representation:
            representation['receipt_name'] = [r['name'] for r in representation['receipts']]
            representation['receipt_value'] = [r['value'] for r in representation['receipts']]
        
        return representation