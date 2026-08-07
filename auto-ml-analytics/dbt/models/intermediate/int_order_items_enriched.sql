select
    i.order_id,
    i.product_id,
    p.category,
    p.price as product_price,
    i.quantity,
    i.unit_price,
    i.total_price,
    o.customer_id,
    o.order_date
from {{ ref('stg_order_items') }} i
left join {{ ref('stg_products') }} p on i.product_id = p.product_id
left join {{ ref('stg_orders') }} o on i.order_id = o.order_id
