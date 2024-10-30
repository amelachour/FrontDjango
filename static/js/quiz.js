    document.getElementById('generate-quiz-btn').addEventListener('click', function() {
        const courseId = this.getAttribute('data-course-id');
        
        fetch(`/cours/courses/${courseId}/generate_quiz/`, {
            method: 'GET',
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json(); // or response.text() if your endpoint returns plain text
        })
        .then(data => {
            // Handle successful quiz generation here
            console.log(data);
            document.getElementById('quiz-container').innerHTML = data.quiz; // Example
        })
        .catch(error => {
            console.error('There was a problem with your fetch operation:', error);
        });
    });
