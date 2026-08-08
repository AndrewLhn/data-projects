with cohorts as (
    select
        customer_id,
        date_trunc('month', min(order_date)) as cohort_month
    from {{ ref('stg_orders') }}
    group by customer_id
),
orders as (
    select
        o.customer_id,
        c.cohort_month,
        date_trunc('month', o.order_date) as order_month
    from {{ ref('stg_orders') }} o
    left join cohorts c on o.customer_id = c.customer_id
),
cohort_size as (
    select cohort_month, count(distinct customer_id) as total
    from cohorts
    group by cohort_month
),
retention_data as (
    select
        o.cohort_month,
        o.order_month,
        count(distinct o.customer_id) as active,
        cs.total as cohort_size
    from orders o
    join cohort_size cs on o.cohort_month = cs.cohort_month
    group by o.cohort_month, o.order_month, cs.total
)
select
    cohort_month,
    order_month,
    active,
    cohort_size,
    (active::float / cohort_size) * 100 as retention_rate
from retention_data
order by cohort_month, order_month
