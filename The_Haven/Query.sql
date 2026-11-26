-- 1. Revenue Trajectory Analysis (Periodical Weekly / Monthly / Yearly)
SELECT strftime('%Y-%m', p.payment_time) AS revenue_period, COUNT(p.payment_id) AS transactions, ROUND(SUM(p.amount), 2) AS total_revenue FROM payment p WHERE p.payment_status = 'Success' GROUP BY revenue_period ORDER BY revenue_period ASC;

-- 2. Revenue Segmentation Across All Facilities, Rooms & Mini Bar
SELECT bi.item_category AS segment_name, COUNT(bi.item_id) AS billing_count, ROUND(SUM(bi.amount), 2) AS segment_revenue, ROUND(SUM(bi.amount) * 100.0 / (SELECT SUM(amount) FROM billing_item), 2) AS revenue_percentage FROM billing_item bi GROUP BY bi.item_category ORDER BY segment_revenue DESC;

-- 3. Top 5 Revenue-Producing VIP Clients (Dynamic Scope Selection)
SELECT c.customer_id, u.full_name, c.organization_name, COUNT(DISTINCT r.reservation_id) AS completed_room_stays, ROUND(SUM(p.amount), 2) AS total_spent FROM customer c JOIN user u ON c.user_id = u.user_id JOIN billing_account ba ON c.customer_id = ba.customer_id JOIN payment p ON ba.account_id = p.account_id LEFT JOIN room_reservation r ON ba.account_id = r.billing_account_id WHERE p.payment_status = 'Success' GROUP BY c.customer_id, u.full_name, c.organization_name ORDER BY total_spent DESC LIMIT 5;

-- 4. Facility Usage Frequency Share and Traffic Footprint
SELECT f.facility_name, f.facility_type, COUNT(ful.log_id) AS visit_count, ROUND(COUNT(ful.log_id) * 100.0 / (SELECT COUNT(*) FROM facility_usage_log), 2) AS usage_frequency_pct FROM facility f LEFT JOIN facility_usage_log ful ON f.facility_id = ful.facility_id GROUP BY f.facility_id, f.facility_name, f.facility_type ORDER BY visit_count DESC;

-- 5. Associate Service Excellence & Hospitality Rating Benchmark
SELECT s.staff_id, u.full_name, s.department, COUNT(sf.feedback_id) AS total_reviews, ROUND(AVG(sf.rating), 2) AS average_rating FROM staff s JOIN user u ON s.user_id = u.user_id LEFT JOIN service_feedback sf ON s.staff_id = sf.staff_id GROUP BY s.staff_id, u.full_name, s.department HAVING total_reviews > 0 ORDER BY average_rating DESC;

-- 6. Room Availability Matrix Across Wings
SELECT rt.type_name, COUNT(r.room_id) AS total_rooms, SUM(CASE WHEN r.status = 'Clean/Vacant' THEN 1 ELSE 0 END) AS available_rooms, SUM(CASE WHEN r.status = 'Occupied' THEN 1 ELSE 0 END) AS occupied_rooms, ROUND(SUM(CASE WHEN r.status = 'Occupied' THEN 1 ELSE 0 END) * 100.0 / COUNT(r.room_id), 1) AS current_occupancy_rate FROM room r JOIN room_type rt ON r.room_type_id = rt.type_id GROUP BY rt.type_id, rt.type_name;

-- 7. Unsettled Guest Folios and Open Accounts Receivable
SELECT ba.account_id, u.full_name, u.phone, u.email, ba.total_charges, ba.total_paid, (ba.total_charges - ba.total_paid) AS outstanding_balance FROM billing_account ba JOIN customer c ON ba.customer_id = c.customer_id JOIN user u ON c.user_id = u.user_id WHERE (ba.total_charges - ba.total_paid) > 0 ORDER BY outstanding_balance DESC;

-- 8. Work Order Status Grouping and Resolution Progress
SELECT status, COUNT(request_id) AS total_count FROM room_request GROUP BY status;

-- 9. Mini Bar Consumption Breakdown
SELECT bi.item_category, COUNT(bi.item_id) AS total_orders, ROUND(AVG(bi.amount), 2) AS avg_ticket_size, ROUND(SUM(bi.amount), 2) AS total_minibar_yield FROM billing_item bi WHERE bi.item_category = 'Mini Bar' GROUP BY bi.item_category;