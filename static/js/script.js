function viewGrades(studentId) {
    fetch(`/view_grades/${studentId}`)
        .then(response => response.json())
        .then(data => {
            let gradesList = "<ul>";
            data.forEach(grade => {
                gradesList += `<li>Grade: ${grade[1]}, Date: ${grade[2]}, PDF: ${grade[3]}</li>`;
            });
            gradesList += "</ul>";
            document.getElementById("grades-list").innerHTML = gradesList;
        });
}