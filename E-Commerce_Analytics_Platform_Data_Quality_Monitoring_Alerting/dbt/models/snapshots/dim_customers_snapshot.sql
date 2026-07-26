{% snapshot dim_customers_snapshot %}
    {{
        config(
            target_schema='snapshots',
            unique_key='customer_id',
            strategy='timestamp',
            updated_at='last_order_date',
            invalidate_hard_deletes=True
        )
    }}
    select * from {{ ref('stg_customers') }}
{% endsnapshot %}
