const englishBtn=document.getElementById("englishBtn");
const tamilBtn=document.getElementById("tamilBtn");

function setEnglish(){

    englishBtn.classList.add("active");
    tamilBtn.classList.remove("active");

    document.getElementById("title").innerText="Krishna Hospital";
    document.getElementById("subtitle").innerText="Child Guidance Centre";
    document.getElementById("description").innerText="Complete your child's registration before visiting the hospital.";
    document.getElementById("trustText").innerText="Secure digital patient registration for Krishna Hospital.";
    document.getElementById("startButton").innerText="Get Started";
}

function setTamil(){

    tamilBtn.classList.add("active");
    englishBtn.classList.remove("active");

    document.getElementById("title").innerText="கிருஷ்ணா மருத்துவமனை";
    document.getElementById("subtitle").innerText="குழந்தைகள் வழிகாட்டல் மையம்";
    document.getElementById("description").innerText="மருத்துவமனைக்கு வருவதற்கு முன் உங்கள் குழந்தையின் பதிவை பூர்த்தி செய்யுங்கள்.";
    document.getElementById("trustText").innerText="கிருஷ்ணா மருத்துவமனைக்கான பாதுகாப்பான டிஜிட்டல் நோயாளர் பதிவு.";
    document.getElementById("startButton").innerText="தொடங்குங்கள்";
}

englishBtn.addEventListener("click",setEnglish);
tamilBtn.addEventListener("click",setTamil);