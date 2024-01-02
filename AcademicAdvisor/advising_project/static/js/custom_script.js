$(document).ready(function () {
    // Retrieve CSRF token from the meta tag
    var csrftoken = $('meta[name="csrf-token"]').attr('content');

    // Event handler for clicking the 'Finish' button on courses
    $('.finish-course').on('click', function () {
        // Retrieve the course ID and AJAX URL from data attributes
        var courseId = $(this).data('courseid');
        var ajaxUrl = $(this).data('ajaxurl').replace('0', courseId);

        $.ajax({
            url: ajaxUrl, // Use the AJAX URL from the button's data attribute
            type: 'POST',
            data: {
                'csrfmiddlewaretoken': csrftoken, // Include CSRF token from meta tag
                'course_id': courseId // Course ID to be marked as completed
            },
            success: function (response) {
                // Log success for debugging
                console.log("Course completion successful", response);

                // Assuming server response includes new progress percentage
                var newPercentage = response.newProgressPercentage;

                // Update the progress bar width and aria-valuenow attribute
                var $progressBar = $('.progress-bar');
                $progressBar.css('width', newPercentage + '%')
                    .attr('aria-valuenow', newPercentage)
                    .text(newPercentage.toFixed(2) + '% Complete');

                // Update the percentage text in the heading, if applicable
                $('#progress-percentage-text').text('You have completed ' + newPercentage.toFixed(2) + '% Towards Graduation');

                // Fade out the row of the finished course
                $('#course-row-' + courseId).fadeOut();
            },
            error: function (xhr, status, error) {
                // Log error for debugging
                console.error("Error in course completion", error);
            }
        });
    });
});

// Scroll Animation Script
window.addEventListener('scroll', () => {
    const sections = document.querySelectorAll('.fade-in-section');
    sections.forEach(section => {
        if (section.getBoundingClientRect().top < window.innerHeight) {
            section.style.animationPlayState = 'running';
        }
    });
});

// Initialize the progress bar on page load
document.addEventListener('DOMContentLoaded', function () {
    var progressBar = document.querySelector('.progress-bar');
    if (progressBar) {
        var progressValue = progressBar.getAttribute('aria-valuenow');
        progressBar.style.width = progressValue + '%';
    }
});

(function (d, m) {
    var kommunicateSettings =
        { "appId": "1a2bc7f99937bb73710a05a99294898c6", "popupWidget": true, "automaticChatOpenOnNavigation": true };
    var s = document.createElement("script"); s.type = "text/javascript"; s.async = true;
    s.src = "https://widget.kommunicate.io/v2/kommunicate.app";
    var h = document.getElementsByTagName("head")[0]; h.appendChild(s);
    window.kommunicate = m; m._globals = kommunicateSettings;
})(document, window.kommunicate || {});

$(document).ready(function () {
    // Initialize autocomplete if the element exists
    if ($("#search-input").length) {
        initializeAutocomplete();
    }
});

$(document).ready(function () {
    if ($('#search-input').length > 0) {
        var autocompleteUrl = $('#search-input').data('autocomplete-url'); // make sure this is a valid endpoint
        var searchUrl = $('#search-input').data('search-url'); // make sure this is a valid endpoint

        $('#search-input').autocomplete({
            source: function (request, response) {
                $.ajax({
                    url: autocompleteUrl,
                    dataType: "json",
                    data: { term: request.term },
                    success: function (data) {
                        response(data); // limit items if necessary
                    }
                });
            },
            select: function (event, ui) {
                // Extract only the course name before the course code in parentheses
                var courseName = ui.item.label.split(" (")[0];
                window.location.href = searchUrl + '?q=' + encodeURIComponent(courseName);
            }
        }).autocomplete("instance")._renderItem = function (ul, item) {
            return $("<li>")
                .append("<div>" + item.label + "<br><span class='category'>" + item.category + "</span></div>")
                .appendTo(ul);
        };
    }

    $(document).on('focus', '.ui-autocomplete-input', function (e) {
        $('.ui-autocomplete').css('z-index', 1050);
    });
});

document.addEventListener('DOMContentLoaded', function () {
    var searchForm = document.getElementById('search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function (e) {
            e.preventDefault(); // Prevent the traditional form submission

            // Collect the data from the form
            var formData = new FormData(searchForm);
            var searchParams = new URLSearchParams(formData).toString();

            // Perform the AJAX request
            fetch(searchForm.action + '?' + searchParams, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'  // Important for Django to recognize AJAX
                }
            })
                .then(response => response.json()) // Parse the JSON returned from the server
                .then(data => {
                    // Now you have your data, you can update the DOM however you like.
                    // This is just an example:
                    updateSearchResults(data);
                    searchForm.reset(); // Resets the form fields if needed
                })
                .catch(error => console.error('Error:', error));
        });
    }
});

function updateSearchResults(data) {
    // Assuming you have divs with ids 'schools', 'majors', and 'courses' for your results
    const schoolsDiv = document.getElementById('schools');
    const majorsDiv = document.getElementById('majors');
    const coursesDiv = document.getElementById('courses');

    // Clear previous results
    schoolsDiv.innerHTML = '';
    majorsDiv.innerHTML = '';
    coursesDiv.innerHTML = '';

    // Parse the JSON data and update the DOM
    const schools = JSON.parse(data.schools);
    schools.forEach(school => {
        schoolsDiv.innerHTML += `<div>${school.fields.name}</div>`;  // Modify as needed
    });

    const majors = JSON.parse(data.majors);
    majors.forEach(major => {
        majorsDiv.innerHTML += `<div>${major.fields.name}</div>`;  // Modify as needed
    });

    const courses = JSON.parse(data.courses);
    courses.forEach(course => {
        coursesDiv.innerHTML += `<div>${course.fields.name} - ${course.fields.course_code}</div>`;  // Modify as needed
    });
}

$(document).ready(function () {
    // Check if the successAlert exists in the current document
    if ($("#successAlert").length) {
        $("#successAlert").show();  // Use jQuery to show the alert
    }
});

var CustomScript = {
    initTutorDashboard: function (config) {
        this.updateUnreadMessagesCount(config.fetchUnreadMessagesUrl);
        setInterval(function () {
            CustomScript.updateUnreadMessagesCount(config.fetchUnreadMessagesUrl);
        }, 30000);
    },

    updateUnreadMessagesCount: function (url) {
        fetch(url)
            .then(response => response.json())
            .then(data => {
                const countElement = document.getElementById("unread-messages-count");
                const noUnreadMessagesElement = document.getElementById("no-unread-messages");
                const unreadMessagesInfoElement = document.getElementById("unread-messages-info");

                countElement.innerText = data.count;
                if (data.count === 0) {
                    noUnreadMessagesElement.style.display = 'block';
                    unreadMessagesInfoElement.style.display = 'none';
                } else {
                    noUnreadMessagesElement.style.display = 'none';
                    unreadMessagesInfoElement.style.display = 'block';
                }
            })
            .catch(error => {
                console.error('Error fetching unread message count:', error);
            });
    },

    redirectToMessagePage: function (studentId, sendMessageUrlTemplate) {
        window.location.href = sendMessageUrlTemplate.replace("{id}", studentId);
    }
};





