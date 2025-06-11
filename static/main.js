let selectedResume = null;
let selectedJobDesc = null;

var loadfile = (event) => {
    
};


const showUpload = (type='resume') => {
    if(type === 'jobDesc') {
        document.getElementsByName('jobDescFile')[0].innerHTML = `<div class="flex items-center justify-between mb-4">
                        <div class="flex items-center gap-3">
                            `+selectedJobDesc.icon+`
                            <div>
                                <p class="font-medium text-gray-800">`+selectedJobDesc.name+`</p>
                                <p class="text-sm text-gray-500">
                                `+(selectedJobDesc.size / 1024).toFixed(1)+` KB
                                </p>
                            </div>
                        </div>
                        <button type="button" onclick="updateFieldDisplay('jobDesc', true)"><i class="bi bi-x-lg"></i></button>
                    </div>`;
    } else {
        document.getElementsByName('resumeFile')[0].innerHTML = `<div class="flex items-center justify-between mb-4">
                        <div class="flex items-center gap-3">
                            `+selectedResume.icon+`
                            <div>
                                <p class="font-medium text-gray-800">`+selectedResume.name+`</p>
                                <p class="text-sm text-gray-500">
                                `+(selectedResume.size / 1024).toFixed(1)+` KB
                                </p>
                            </div>
                        </div>
                        <button type="button" onclick="updateFieldDisplay('resume', true)"><i class="bi bi-x-lg"></i></button>
                    </div>`;
    }
}

const updateFieldDisplay = (type='resume', isClose=false) => {
    if(type === 'jobDesc') {
        if(isClose) {
            document.getElementsByName("jobDescFile")[0].style.display = "none";
            document.getElementsByName("jobInputLabel")[0].style.display = "block";
            document.getElementsByName('jobInput')[0].value = null;
            selectedJobDesc = null;
        } else {
            document.getElementsByName("jobDescFile")[0].style.display = "block";
            document.getElementsByName("jobInputLabel")[0].style.display = "none";
        }
    } else {
        if(isClose) {
            document.getElementsByName("resumeFile")[0].style.display = "none";
            document.getElementsByName("resumeInputLabel")[0].style.display = "block";
            document.getElementsByName('resumeInput')[0].value = null;
            selectedResume = null;
        } else {
            document.getElementsByName("resumeFile")[0].style.display = "block";
            document.getElementsByName("resumeInputLabel")[0].style.display = "none";
        }
    }
}

var addFile = (event, type='resume') => {
    if(type === 'resume') {
        selectedResume = event.target.files[0];
        switch(selectedResume.type){
            case "application/pdf": selectedResume.type = "pdf";
                                    selectedResume.icon = '<i class="bi bi-filetype-pdf text-3xl"></i>';  
                                    break;
            case "text/plain": selectedResume.type = "text";
                                selectedResume.icon = '<i class="bi bi-filetype-txt text-3xl"></i>';
                                break;
            default: selectedResume.type = "docx";
                     selectedResume.icon = '<i class="bi bi-filetype-docx text-3xl"></i>';
        }
        console.log(selectedResume);
    } else {
        selectedJobDesc = event.target.files[0];
        switch(selectedJobDesc.type){
            case "application/pdf": selectedJobDesc.type = "pdf";
                                    selectedJobDesc.icon = '<i class="bi bi-filetype-pdf text-3xl"></i>';  
                                    break;
            case "text/plain": selectedJobDesc.type = "text";
                                selectedJobDesc.icon = '<i class="bi bi-filetype-txt text-3xl"></i>';
                                break;
            default: selectedJobDesc.type = "docx";
                     selectedJobDesc.icon = '<i class="bi bi-filetype-docx text-3xl"></i>';
        }
        console.log(selectedJobDesc);
    }
    updateFieldDisplay(type, false);
    showUpload(type);
}