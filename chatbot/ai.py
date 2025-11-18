# chatbot/ai.py - Enhanced Trashify Assistant
from django.utils import timezone
from datetime import datetime, timedelta
from project.models import Event, WasteReport, User, EventParticipation
from django.db.models import Count

def get_chatbot_response(message):
    message = message.lower()

    # Greetings
    if "hello" in message or "hi" in message or "hey" in message or "good morning" in message or "good evening" in message:
        return "👋 Hello! I'm Trashify Assistant. I'm here to help you with waste management and environmental questions. How can I assist you today?"
    
    # Website Navigation
    elif "home" in message or "homepage" in message:
        return "🏠 The homepage shows our crime analytics platform with interactive features, data visualizations, and analysis tools for law enforcement and policy makers!"
    
    elif "analysis" in message or "analytics" in message:
        return "📊 Our analytics include: Single Crime Trends, Multi-Crime Comparisons, District Analysis, Crime Hotspots, Cross-State Analysis, and Enhanced Visualizations!"
    
    elif "data" in message or "dataset" in message:
        return "📁 We analyze 7 comprehensive datasets covering IPC crimes, cyber crimes, crimes against women, juvenile crimes, and missing persons across 35+ Indian states (2017-2022)!"
    
    elif "about" in message or "about us" in message:
        return "ℹ️ Suraksha Analytics is a comprehensive crime data analysis platform empowering law enforcement and policy makers with data-driven insights for safer communities."
    
    elif "mission" in message:
        return "🎯 Our mission is to empower law enforcement agencies and policy makers with advanced crime data analytics to create safer communities through data-driven decision making."
    
    elif "vision" in message:
        return "👁️ Our vision is a safer India where crime prevention and law enforcement are enhanced through intelligent data analysis and predictive insights."
    
    # Crime Data Analysis
    elif "crime" in message and "trend" in message:
        return "📈 Crime Trend Analysis: Analyze time-series data for specific crime types, identify patterns, seasonal variations, and long-term trends across different regions!"
    
    elif "hotspot" in message or "hot spot" in message:
        return "🔥 Crime Hotspots: Identify high-risk areas with concentrated criminal activity. Our analysis helps law enforcement allocate resources effectively!"
    
    elif "district" in message or "state" in message:
        return "🗺️ Geographic Analysis: Compare crime statistics across districts and states. Understand regional crime patterns and jurisdictional differences!"
    
    # User Roles & Dashboards
    elif "user" in message and "dashboard" in message:
        return "👤 User Dashboard shows: Your waste reports, points earned, completion status, and environmental impact. Access it after logging in!"
    
    elif "admin" in message and "dashboard" in message:
        return "👨‍💼 Admin Dashboard (for admins only): Manage users, assign reports to crew members, view analytics, handle contact messages, and organize events."
    
    elif "crew" in message and "dashboard" in message:
        return "👷 Crew Dashboard (for crew members): View assigned cleanup tasks, update task status, track completion rates, and manage work assignments."
    
    elif "volunteer" in message and "dashboard" in message:
        return "🤝 Volunteer Dashboard: View assigned reports, accept/reject cleanup tasks, track your volunteer activities, and see your community impact."
    
    # Events & Community - Dynamic responses
    elif "event" in message or "cleanup" in message or "drive" in message:
        try:
            upcoming_events = Event.objects.filter(date__gte=timezone.now().date()).order_by('date')[:3]
            if upcoming_events:
                event_list = "\n".join([f"• {event.title} - {event.date} at {event.time} ({event.location})" for event in upcoming_events])
                return f"🌱 Upcoming Events:\n{event_list}\n\nVisit 'Events' page to register and participate!"
            else:
                return "🌱 No upcoming events scheduled. Check back soon for cleanup drives, workshops, and tree planting events!"
        except:
            return "🌱 Join cleanup events! Visit 'Events' page to see upcoming drives: beach cleanups, tree planting, recycling drives. Register to participate!"
    
    elif "organize" in message and "event" in message:
        return "📅 Admins can organize events through the admin dashboard. Create cleanup drives, workshops, awareness campaigns, and tree planting events."
    
    elif "participate" in message or "join event" in message:
        return "✋ To join events: 1) Visit Events page 2) Choose an event 3) Fill registration form 4) Get approved 5) Participate and make a difference!"
    
    elif "scheduled" in message or "upcoming" in message:
        try:
            upcoming_events = Event.objects.filter(date__gte=timezone.now().date()).order_by('date')[:5]
            if upcoming_events:
                event_details = "\n".join([f"📅 {event.title}\n   Date: {event.date}\n   Time: {event.time}\n   Location: {event.location}\n   Type: {event.get_event_type_display()}\n" for event in upcoming_events])
                return f"📋 Scheduled Events:\n{event_details}Visit Events page to register!"
            else:
                return "📋 No events currently scheduled. New events are added regularly - check back soon!"
        except:
            return "📋 Check the Events page for scheduled activities and upcoming cleanup drives!"
    
    # Points & Rewards
    elif "points" in message or "reward" in message or "earn" in message:
        return "🏆 Earn points: 5 points per waste report! Points show your environmental contribution. Check the leaderboard to see top contributors!"
    
    elif "leaderboard" in message or "ranking" in message or "top" in message:
        return "🥇 Leaderboard shows top environmental contributors ranked by points. Compete with others and see your community impact ranking!"
    
    # Waste Types & Management
    elif "plastic" in message:
        return "🚫 Plastic waste: Report plastic accumulation, use reusable alternatives, avoid single-use plastics. Proper disposal prevents ocean pollution!"
    
    elif "organic" in message or "compost" in message or "food waste" in message:
        return "🌿 Organic waste: Compost kitchen scraps and yard waste. Creates nutrient-rich soil and reduces landfill burden. Report large organic waste piles!"
    
    elif "electronic" in message or "e-waste" in message or "electronics" in message:
        return "💻 E-waste (phones, computers, batteries): Never throw in regular trash! Report e-waste accumulation for proper recycling and safe disposal."
    
    elif "hazardous" in message or "dangerous" in message or "chemical" in message:
        return "⚠️ Hazardous waste (chemicals, batteries, paint): Extremely dangerous! Report immediately for specialized cleanup. Never handle personally!"
    
    elif "construction" in message or "debris" in message:
        return "🏗️ Construction debris: Report illegal dumping of construction waste. Requires special handling and disposal methods."
    
    # Recycling & Environment
    elif "recycle" in message or "recycling" in message:
        return "♻️ Recycling tips: Separate materials (plastic, paper, glass, metal), clean containers, check local guidelines. Reduce, Reuse, then Recycle!"
    
    elif "environment" in message or "climate" in message or "green" in message:
        return "🌍 Every action counts! Proper waste management reduces pollution, protects wildlife, fights climate change. Join our green community!"
    
    elif "pollution" in message or "contamination" in message:
        return "🚨 Pollution prevention: Report waste before it spreads, participate in cleanups, educate others. Together we can reduce environmental contamination!"
    
    # Crew & Jobs
    elif "crew" in message or "job" in message or "work" in message or "employment" in message:
        return "👷 Join our crew! Crew members are professional waste management staff with employee IDs. Contact admin for employment opportunities!"
    
    elif "assign" in message or "task" in message:
        return "📋 Task assignment: Admins assign waste reports to crew members and volunteers. Check your dashboard for assigned cleanup tasks!"
    
    # Contact & Support
    elif "contact" in message or "support" in message or "help" in message:
        return "📞 Need help? Visit 'Contact Us' page to send a message to our team. Admins will respond to your inquiries promptly!"
    
    elif "email" in message:
        return "📧 Contact email: TrashifyClean@gmail.com - Send us your questions, suggestions, or report issues. We're here to help!"
    
    elif "phone" in message or "call" in message:
        return "📱 Contact phone: +91 8510962962 - Call us for urgent waste management issues or general inquiries about our platform."
    
    # Technical & Features
    elif "mobile" in message or "app" in message or "phone" in message:
        return "📱 Trashify works on mobile browsers! Access all features on your phone: report waste, view dashboard, join events, earn points!"
    
    elif "notification" in message or "alert" in message:
        return "🔔 Get updates on your reports, event notifications, and point earnings. Stay connected with your environmental impact!"
    
    elif "status" in message or "progress" in message:
        return "📊 Track status: Reports go from Pending → Assigned → In Progress → Completed. Monitor your environmental contributions!"
    
    # Statistics & Analytics - Dynamic data
    elif "statistics" in message or "stats" in message or "numbers" in message:
        return "📈 Platform Statistics:\n• 20,000+ Crime Records\n• 35+ Indian States\n• 700+ Districts\n• 5 Crime Categories\n• 6 Years Coverage (2017-2022)\n• Multiple Analysis Types!"
    
    elif "impact" in message or "contribution" in message:
        try:
            recent_reports = WasteReport.objects.filter(created_at__gte=timezone.now() - timedelta(days=7)).count()
            return f"🌟 Recent Impact: {recent_reports} waste reports submitted this week! Track your personal reports, points earned, and events joined in your dashboard!"
        except:
            return "🌟 Your impact: Track reports submitted, points earned, events joined. See how you're making a difference in your community!"
    
    # Troubleshooting
    elif "problem" in message or "issue" in message or "error" in message or "bug" in message:
        return "🔧 Having issues? Contact us through the Contact page with details. Our team will help resolve any technical problems!"
    
    elif "forgot" in message and "password" in message:
        return "🔑 Forgot password? Contact our support team through the Contact page. We'll help you regain access to your account!"
    
    elif "account" in message or "profile" in message:
        return "👤 Account management: View your profile in the dashboard, track your activities, and monitor your environmental contributions!"
    
    # Closing
    elif "bye" in message or "thank you" in message or "thanks" in message or "goodbye" in message:
        try:
            user_count = User.objects.count()
            return f"😊 You're welcome! Join our community of {user_count}+ environmental champions. Keep up the great work protecting our environment. Feel free to chat anytime. Have a green day! 🌱"
        except:
            return "😊 You're welcome! Keep up the great work protecting our environment. Feel free to chat anytime. Have a green day! 🌱"
    
    # Website features and navigation
    elif "features" in message or "what can" in message or "capabilities" in message:
        return "🚀 Suraksha Analytics Features:\n• Crime Trend Analysis\n• Multi-Crime Comparisons\n• Geographic Intelligence\n• Crime Hotspot Detection\n• Statistical Analysis\n• Interactive Visualizations\n• Cross-State Analysis\n• Real-time Filtering\n• Data Export Options\n\nWhat would you like to explore?"
    
    elif "how to use" in message or "getting started" in message:
        return "🎯 Getting Started:\n1. Visit the homepage\n2. Click 'Start Analysis'\n3. Choose analysis type\n4. Select filters (state, district, year)\n5. View interactive results\n6. Export data if needed\n\nNeed help with any specific analysis?"
    
    elif "today" in message or "this week" in message:
        try:
            today_reports = WasteReport.objects.filter(created_at__date=timezone.now().date()).count()
            week_reports = WasteReport.objects.filter(created_at__gte=timezone.now() - timedelta(days=7)).count()
            today_events = Event.objects.filter(date=timezone.now().date()).count()
            return f"📊 Today's Activity:\n• New Reports: {today_reports}\n• This Week's Reports: {week_reports}\n• Events Today: {today_events}\n\nStay active and make a difference!"
        except:
            return "📊 Check your dashboard for today's activities and recent community contributions!"
    
    # Default response
    else:
        return "🤖 I can help with: waste reporting, user accounts, events, points system, recycling tips, contact info, dashboards, crew jobs, statistics, and environmental questions. What would you like to know?"