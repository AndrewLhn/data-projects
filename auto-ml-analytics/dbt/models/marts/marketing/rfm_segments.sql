with customer_metrics as (
    select
        customer_id,
        max(order_date) as last_order_date,
        count(distinct order_id) as frequency,
        sum(total_price) as monetary
    from {{ ref('int_order_items_enriched') }}
    group by customer_id
),
rfm_scores as (
    select
        customer_id,
        ntile(5) over (order by last_order_date desc) as recency,
        ntile(5) over (order by frequency asc) as frequency,
        ntile(5) over (order by monetary asc) as monetary
    from customer_metrics
)
select
    customer_id,
    recency,
    frequency,
    monetary,
    (recency + frequency + monetary) as total_rfm,
    case
        when recency = 5 and frequency >= 4 and monetary >= 4 then 'Champions'
        when recency >= 4 and frequency >= 3 and monetary >= 3 then 'Loyal'
        when recency = 5 and frequency <= 2 and monetary <= 2 then 'New Loyal'
        when recency = 4 and frequency <= 2 and monetary <= 2 then 'Promising'
        when recency = 3 and frequency >= 3 and monetary >= 3 then 'Need Attention'
        when recency <= 2 and frequency <= 2 and monetary <= 2 then 'At Risk'
        else 'Other'
    end as segment
from rfm_scores
