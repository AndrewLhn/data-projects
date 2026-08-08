with monthly as (
    select
        date_trunc('month', order_date) as month,
        sum(total_price) as revenue
    from {{ ref('int_order_items_enriched') }}
    group by month
)
select
    month,
    revenue,
    lag(revenue, 1) over (order by month) as prev_month_revenue,
    lag(revenue, 12) over (order by month) as prev_year_revenue,
    (revenue - lag(revenue, 1) over (order by month)) / lag(revenue, 1) over (order by month) * 100 as mom_growth,
    (revenue - lag(revenue, 12) over (order by month)) / lag(revenue, 12) over (order by month) * 100 as yoy_growth
from monthly
