import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'advising_project.settings')
django.setup()
from django.contrib.auth.hashers import make_password
from advising_app.models import School, Major, Course, CustomUser

tutor_user = CustomUser.objects.create(
    username='tutor1',
    email='tutor1@example.com',
    first_name='Jane',
    last_name='Doe',
    is_tutor=True,
    password=make_password('your_tutor_password_here')
)

tutor_user.save()

manager_user = CustomUser.objects.create(
    username='manager1',
    email='manager1@example.com',
    first_name='Michael',
    last_name='Smith',
    is_manager=True,
    password=make_password('your_manager_password_here')
)

manager_user.save()


student_user = CustomUser.objects.create(
    username='student1',
    email='student1@example.com',
    first_name='John',
    last_name='Doe',
    is_student=True,
    password=make_password('your_password_here')
)

student_user.save()


# Create schools
school1 = School(name="School of ICT")
school2 = School(name="School of Business")
school3 = School(name="School of Logistics")
school4 = School(name="School of Engineering")
school5 = School(name="School of Creative Media")

school1.save()
school2.save()
school3.save()
school4.save()
school5.save()

# Create major
#ICT majors
major1 = Major(name="Programming", description="This major is for learning new programming languages.", major_credit= 480, major_code="ICT8011", school=school1)
major2 = Major(name="Networking", description="This major is for learning new programming languages.",major_credit= 480, major_code="ICT8031", school=school1)
major3 = Major(name="Information Security", description="This major is for learning new programming languages.", major_credit= 480, major_code="ICT8022",school=school1)
major4 = Major(name="Cybersecurity", description="This major is for learning new programming languages.", major_credit= 480, major_code="ICT8051",school=school1)
major5 = Major(name="Database Systems", description="This major is for learning new programming languages.", major_credit= 480, major_code="ICT8041",school=school1)
#Buisniss majors
major6 = Major(name="Digital Marketing", description="Develop digital and social media marketing campaigns to deliver marketing objectives.", major_credit= 480, major_code="DMK8012", school=school2)
major7 = Major(name="Financial Technology", description="To apply financial technology knowledge to develop new technological innovations and solutions.",major_credit= 480, major_code="BFT8100", school=school2)
major8 = Major(name="Business (General)", description="Demonstrate a detailed knowledge of core business concepts and a broad understanding of the changing business environment", major_credit= 480, major_code="BBS8000",school=school2)
major9 = Major(name="Banking and Finance", description="Apply the fundamentals of circulation of money, credit and investment in order to ensure appropriate organizational growth", major_credit= 480, major_code="BBS8030",school=school2)
major10 = Major(name="Human Resource Management", description="Demonstrate a detailed knowledge of core business concepts and a broad understanding of the changing business environment", major_credit= 480, major_code="BBS8070",school=school2)

major1.save()
major2.save()
major3.save()
major4.save()
major5.save()
major6.save()
major7.save()
major8.save()
major9.save()
major10.save()

# Create courses
course1 = Course(
    name="Computer Programming 1", 
    course_description="This major is for learning new programming languages", 
    course_code="IT6004", 
    course_credits=15, 
    semester="semesterB", 
    nqf_lvl=7,
    year=1
    )
course1.save()

course2 = Course(
    name="Computer Programming 2", 
    course_description="This subject teaches you Java",
    course_code="IT7008", 
    course_credits=15, 
    semester="semesterB",
    nqf_lvl=7,
    year=2
      )
course2.save()

course3 = Course(
    name="Maths for Computing",
    course_description="This major is for learning new programming languages",
    course_code="IT6004",
    course_credits=15,
    semester="semesterA",
    nqf_lvl=7,
    year=1
          )
course3.save()

course4 = Course(
    name="Unix Systems", 
    course_description="This major is for learning new programming languages", 
    course_code="IT6004", 
    course_credits=15, 
    semester="semesterA", 
    nqf_lvl=7,
    year=1
    )
course4.save()

course5 = Course(
    name="Information Security", 
    course_description="This major is for learning new programming languages", 
    course_code="IT6004", 
    course_credits=15, 
    semester="semesterA", 
    nqf_lvl=7,
    year=2
    )
course5.save()

course6 = Course(
    name="Web Fundamentals", 
    course_description="This major is for learning new programming languages", 
    course_code="IT6004", 
    course_credits=15, 
    semester="semesterA", 
    nqf_lvl=7,
    year=2
    )
course6.save()

course7 = Course(name="System Analysis and Design", course_description="This major is for learning new programming languages", course_code="IT6004", course_credits=15, semester="semesterA", nqf_lvl=7, year=2)
course7.save()
course8 = Course(name="Database Programming 2",course_description="Advanced database programming and management.",course_code="IT6019",course_credits=15,semester="semesterB",nqf_lvl=7, year=3)
course8.save()

course9 = Course(
    name="Games Development",
    course_description="Learn to design and develop interactive games.",
    course_code="IT6020",
    course_credits=15,
    semester="semesterB",
    nqf_lvl=7,
    year=3
)
course9.save()

course10 = Course(
    name="Advanced Programming",
    course_description="Advanced programming concepts and techniques.",
    course_code="IT6021",
    course_credits=15,
    semester="semesterB",
    nqf_lvl=7,
    year=3
)
course10.save()

course11 = Course(
    name="IT Project Management",
    course_description="Learn project management in IT contexts.",
    course_code="IT6022",
    course_credits=15,
    semester="semesterA",
    nqf_lvl=7,
    year=4
)
course11.save()

course12 = Course(
    name="Cooperative Learning Project",
    course_description="Collaborative project-based learning experience.",
    course_code="IT6023",
    course_credits=15,
    semester="semesterB",
    nqf_lvl=7,
    year=4
)
course12.save()

course13 = Course(
    name="Research Project",
    course_description="Conduct research and complete a research project.",
    course_code="IT6024",
    course_credits=15,
    semester="semesterB",
    nqf_lvl=7,
    year=4
)
course13.save()

course14 = Course(
    name="Entrepreneurship Lean Start up",
    course_description="Learn entrepreneurship and lean startup principles.",
    course_code="IT6025",
    course_credits=15,
    semester="semesterB",
    nqf_lvl=7,
    year=4
)
course14.save()

course15 = Course(
    name="Object-Oriented Design",
    course_description="Object-Oriented Design to learn more about system design",
    course_code="IT7006",
    course_credits=15,
    semester="semesterA",
    nqf_lvl=7,
    year=3
)
course15.save()

course16 = Course(
    name="Mobile Programming",
    course_description="Object-Oriented Design to learn more about system design",
    course_code="IT8108",
    course_credits=15,
    semester="semesterA",
    nqf_lvl=7,
    year=3
)
course16.save()

course17 = Course(
    name="Database Systems 1",
    course_description="Object-Oriented Design to learn more about system design",
    course_code="IT6005",
    course_credits=15,
    semester="semesterB",
    nqf_lvl=7,
    year=1
)
course17.save()

course18 = Course(
    name="Database Systems 2",
    course_description="Object-Oriented Design to learn more about system design",
    course_code="IT7005",
    course_credits=15,
    semester="semesterB",
    nqf_lvl=7,
    year=2
)
course18.save()

course19 = Course(
    name="Computer Systems",
    course_description="Object-Oriented Design to learn more about system design",
    course_code="IT6001",
    course_credits=15,
    semester="semesterA",
    nqf_lvl=7,
    year=1
)
course19.save()

course20 = Course(
    name="Networks and Data Communications",
    course_description="Object-Oriented Design to learn more about system design",
    course_code="IT6003",
    course_credits=15,
    semester="semesterB",
    nqf_lvl=7,
    year=1
)
course20.save()

course21 = Course(
    name="Web Development with Non-relational databases",
    course_description="Object-Oriented Design to learn more about system design",
    course_code="IT7405",
    course_credits=15,
    semester="semesterA",
    nqf_lvl=7,
    year=3
)
course21.save()

course22 = Course(
    name="Database Administration",
    course_description="Object-Oriented Design to learn more about system design",
    course_code="IT7405",
    course_credits=15,
    semester="semesterA",
    nqf_lvl=7,
    year=3
)
course22.save()

course23 = Course(
    name="Data Mining",
    course_description="Object-Oriented Design to learn more about system design",
    course_code="IT8416",
    course_credits=15,
    semester="semesterB",
    nqf_lvl=7,
    year=3
)
course23.save()

# Specify prerequisites
course5.prerequisites.add(course4)  # Unix Systems is a prerequisite for Information Security
course7.prerequisites.add(course3)  # Database Systems 1 is a prerequisite for System Analysis and Design
course7.prerequisites.add(course8)  # Database Systems 2 is a prerequisite for System Analysis and Design
course8.prerequisites.add(course3)  # Database Systems 1 is a prerequisite for Database Programming 2
course8.prerequisites.add(course2)  # Computer Programming 2 is a prerequisite for Database Programming 2
course10.prerequisites.add(course7)  # System Analysis and Design is a prerequisite for Advanced Programming
course10.prerequisites.add(course2)  # Computer Programming 2 is a prerequisite for Advanced Programming
course9.prerequisites.add(course2)  # Computer Programming 2 is a prerequisite for Games Development
course9.prerequisites.add(course10)  # Advanced Programming is a prerequisite for Games Development
course9.prerequisites.add(course8)  # Database Programming 2 is a prerequisite for Games Development
course11.prerequisites.add(course7)  # System Analysis and Design is a prerequisite for IT Project Management
course12.prerequisites.add(course11)  # IT Project Management is a prerequisite for Cooperative Learning Project
course13.prerequisites.add(course11)  # IT Project Management is a prerequisite for Research Project
course14.prerequisites.add(course11)  # IT Project Management is a prerequisite for Entrepreneurship Lean Start-up

# Save the courses with prerequisites
course5.save()
course7.save()
course8.save()
course9.save()
course10.save()
course11.save()
course12.save()
course13.save()
course14.save()


# Add courses to major
major1.courses.add(course1, course2, course3, course4, course5, course6, course7, course8, course9, course10, course11, course12, course13, course14, course15, course16,
                   course17,course18,course19,course20)
major1.save()

major5.courses.add(course1,course2,course3,course4,course5,course6,course7,course8,course10,course11,course12,course13,course14,course17,course18,course19,course20,course21,course22,course23)
major5.save()
