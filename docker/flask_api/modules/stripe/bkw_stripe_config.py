import os

trial_days = 14

stripe_api_key = os.environ['STRIPE_API_KEY']
stripe_webhook_secret = os.environ['STRIPE_WEBHOOK_SECRET']
return_url = os.environ['STRIPE_RETURN_URL']

subscription_price_levels = [
    {'product_name': 'individual', 'product_level': 1},
    {'product_name': 'team', 'product_level': 2},
    {'product_name': 'mvp', 'product_level': 3}
]

event_data = {
  "id": "evt_1MdhUpCWYsrvqullvCutjMEu",
  "object": "event",
  "api_version": "2020-08-27",
  "created": 1676930765,
  "data": {
    "object": {
      "id": "sub_1MdhUmCWYsrvqullpB014XRJ",
      "object": "subscription",
      "application": None,
      "application_fee_percent": None,
      "automatic_tax": {
        "enabled": False
      },
      "billing_cycle_anchor": 1676930764,
      "billing_thresholds": None,
      "cancel_at": None,
      "cancel_at_period_end": False,
      "canceled_at": None,
      "collection_method": "charge_automatically",
      "created": 1676930764,
      "currency": "usd",
      "current_period_end": 1679349964,
      "current_period_start": 1676930764,
      "customer": "cus_NOUTyCRvyjKP3s",
      "days_until_due": None,
      "default_payment_method": None,
      "default_source": None,
      "default_tax_rates": [
      ],
      "description": None,
      "discount": None,
      "ended_at": None,
      "items": {
        "object": "list",
        "data": [
          {
            "id": "si_NOUTBbqOOfdalV",
            "object": "subscription_item",
            "billing_thresholds": None,
            "created": 1676930764,
            "metadata": {
            },
            "plan": {
              "id": "price_1MH7YoCWYsrvqullA5T3Td2y",
              "object": "plan",
              "active": True,
              "aggregate_usage": None,
              "amount": 19900,
              "amount_decimal": "19900",
              "billing_scheme": "per_unit",
              "created": 1671549414,
              "currency": "usd",
              "interval": "month",
              "interval_count": 1,
              "livemode": True,
              "metadata": {
                "product_name": "individual"
              },
              "nickname": None,
              "product": "prod_N19slOlHayTi95",
              "tiers_mode": None,
              "transform_usage": None,
              "trial_period_days": None,
              "usage_type": "licensed"
            },
            "price": {
              "id": "price_1MH7YoCWYsrvqullA5T3Td2y",
              "object": "price",
              "active": True,
              "billing_scheme": "per_unit",
              "created": 1671549414,
              "currency": "usd",
              "custom_unit_amount": None,
              "livemode": True,
              "lookup_key": None,
              "metadata": {
                "product_name": "individual"
              },
              "nickname": None,
              "product": "prod_N19slOlHayTi95",
              "recurring": {
                "aggregate_usage": None,
                "interval": "month",
                "interval_count": 1,
                "trial_period_days": None,
                "usage_type": "licensed"
              },
              "tax_behavior": "exclusive",
              "tiers_mode": None,
              "transform_quantity": None,
              "type": "recurring",
              "unit_amount": 19900,
              "unit_amount_decimal": "19900"
            },
            "quantity": 1,
            "subscription": "sub_1MdhUmCWYsrvqullpB014XRJ",
            "tax_rates": [
            ]
          }
        ],
        "has_more": False,
        "total_count": 1,
        "url": "/v1/subscription_items?subscription=sub_1MdhUmCWYsrvqullpB014XRJ"
      },
      "latest_invoice": "in_1MdhUmCWYsrvqullxmQIMkPJ",
      "livemode": True,
      "metadata": {
      },
      "next_pending_invoice_item_invoice": None,
      "on_behalf_of": None,
      "pause_collection": None,
      "payment_settings": {
        "payment_method_options": None,
        "payment_method_types": None,
        "save_default_payment_method": "off"
      },
      "pending_invoice_item_interval": None,
      "pending_setup_intent": None,
      "pending_update": None,
      "plan": {
        "id": "price_1MH7YoCWYsrvqullA5T3Td2y",
        "object": "plan",
        "active": True,
        "aggregate_usage": None,
        "amount": 19900,
        "amount_decimal": "19900",
        "billing_scheme": "per_unit",
        "created": 1671549414,
        "currency": "usd",
        "interval": "month",
        "interval_count": 1,
        "livemode": True,
        "metadata": {
          "product_name": "individual"
        },
        "nickname": None,
        "product": "prod_N19slOlHayTi95",
        "tiers_mode": None,
        "transform_usage": None,
        "trial_period_days": None,
        "usage_type": "licensed"
      },
      "quantity": 1,
      "schedule": None,
      "start_date": 1676930764,
      "status": "incomplete",
      "test_clock": None,
      "transfer_data": None,
      "trial_end": None,
      "trial_settings": {
        "end_behavior": {
          "missing_payment_method": "cancel"
        }
      },
      "trial_start": None
    }
  },
  "livemode": True,
  "pending_webhooks": 1,
  "request": {
    "id": "req_zBHe8SFLta8bno",
    "idempotency_key": "78ac86ba-832a-44a4-a1c5-5ff5024083d7"
  },
  "type": "customer.subscription.created"
}