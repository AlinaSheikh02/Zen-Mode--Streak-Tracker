document.addEventListener('DOMContentLoaded', () => {
    const addSubjectButton = document.getElementById('add-subject');
    const subjectNameInput = document.getElementById('subject-name');
    const subjectsList = document.getElementById('subjects-list');
    const logsList = document.getElementById('logs-list');
    
    const apiUrl = 'http://127.0.0.1:5000';

    // Fetch and display subjects
    function fetchSubjects() {
        fetch(`${apiUrl}/api/subjects`)
            .then(response => response.json())
            .then(data => {
                subjectsList.innerHTML = '';
                data.forEach(subject => {
                    const li = document.createElement('li');
                    li.textContent = subject.name;
                    subjectsList.appendChild(li);
                });
            });
    }

    // Add a new subject
    addSubjectButton.addEventListener('click', () => {
        const subjectName = subjectNameInput.value;
        if (subjectName) {
            fetch(`${apiUrl}/add_subject`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ subject_name: subjectName }),
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                fetchSubjects();
            })
            .catch(error => console.error('Error adding subject:', error));
        } else {
            alert('Please enter a subject name.');
        }
    });

    // Fetch and display logs for a specific subject
    function fetchLogs() {
        fetch(`${apiUrl}/get_all_logs`)
            .then(response => response.json())
            .then(data => {
                logsList.innerHTML = '';
                Object.keys(data).forEach(subjectId => {
                    const subject = data[subjectId];
                    const div = document.createElement('div');
                    const subjectName = document.createElement('h4');
                    subjectName.textContent = subject.name;
                    div.appendChild(subjectName);
                    subject.notes.forEach(note => {
                        const p = document.createElement('p');
                        p.textContent = `${note.timestamp}: ${note.note}`;
                        div.appendChild(p);
                    });
                    logsList.appendChild(div);
                });
            })
            .catch(error => console.error('Error fetching logs:', error));
    }

    fetchSubjects();
    fetchLogs();
});
