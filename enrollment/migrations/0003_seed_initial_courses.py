from django.db import migrations


def seed_courses(apps, schema_editor):
    Course = apps.get_model("enrollment", "Course")
    courses = [
        {"code": "CS101", "title": "Intro to Programming", "description": "Fundamentals of coding with Python, variables, loops, and functions.", "semester": "Fall 2025", "credits": 3, "capacity": 40},
        {"code": "CS102", "title": "Data Structures", "description": "Arrays, stacks, queues, linked lists, trees, graphs, and complexity.", "semester": "Fall 2025", "credits": 3, "capacity": 35},
        {"code": "CS103", "title": "Databases", "description": "Relational modeling, SQL, indexing, and transactions.", "semester": "Spring 2026", "credits": 3, "capacity": 35},
        {"code": "CS104", "title": "Web Development", "description": "Frontend basics with HTML/CSS/JS and backend patterns with Django.", "semester": "Spring 2026", "credits": 3, "capacity": 30},
        {"code": "CS105", "title": "Algorithms", "description": "Design techniques, sorting, searching, greedy, DP, and graph algorithms.", "semester": "Fall 2025", "credits": 3, "capacity": 35},
        {"code": "CS106", "title": "Operating Systems", "description": "Processes, threads, synchronization, memory, and file systems.", "semester": "Spring 2026", "credits": 4, "capacity": 30},
        {"code": "CS107", "title": "Networks", "description": "TCP/IP, routing, HTTP, and basic security concepts.", "semester": "Spring 2026", "credits": 3, "capacity": 30},
        {"code": "CS108", "title": "Software Engineering", "description": "Requirements, design patterns, testing, CI/CD, and agile practices.", "semester": "Fall 2025", "credits": 3, "capacity": 40},
        {"code": "CS109", "title": "Cloud Computing", "description": "Compute, storage, containers, and deployment fundamentals.", "semester": "Spring 2026", "credits": 3, "capacity": 30},
        {"code": "CS110", "title": "Mobile Development", "description": "Building mobile apps with responsive design principles.", "semester": "Fall 2025", "credits": 3, "capacity": 25},
        {"code": "CS111", "title": "AI Fundamentals", "description": "Search, classification, regression, and model evaluation.", "semester": "Spring 2026", "credits": 3, "capacity": 30},
        {"code": "CS112", "title": "Cybersecurity Basics", "description": "Threats, encryption, authentication, and secure coding.", "semester": "Fall 2025", "credits": 3, "capacity": 30},
        {"code": "CS113", "title": "Human-Computer Interaction", "description": "Designing usable and accessible interfaces.", "semester": "Spring 2026", "credits": 3, "capacity": 25},
        {"code": "CS114", "title": "Data Visualization", "description": "Telling stories with data using plots and dashboards.", "semester": "Fall 2025", "credits": 3, "capacity": 25},
        {"code": "CS115", "title": "DevOps Practices", "description": "Version control, CI/CD, monitoring, and observability.", "semester": "Spring 2026", "credits": 3, "capacity": 30},
    ]
    for course in courses:
        Course.objects.update_or_create(code=course["code"], defaults=course)


def unseed_courses(apps, schema_editor):
    Course = apps.get_model("enrollment", "Course")
    codes = [
        "CS101",
        "CS102",
        "CS103",
        "CS104",
        "CS105",
        "CS106",
        "CS107",
        "CS108",
        "CS109",
        "CS110",
        "CS111",
        "CS112",
        "CS113",
        "CS114",
        "CS115",
    ]
    Course.objects.filter(code__in=codes).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("enrollment", "0002_update_course_enrollment_schema"),
    ]

    operations = [
        migrations.RunPython(seed_courses, unseed_courses),
    ]
