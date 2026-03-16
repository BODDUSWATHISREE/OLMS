function registerUser(){

let id = document.getElementById("idNumber").value;
let name = document.getElementById("fullName").value;
let email = document.getElementById("email").value;
let password = document.getElementById("password").value;
let role = document.getElementById("role").value;

if(role === "Student"){

if(!(id.startsWith("N") || id.startsWith("n"))){

alert("Student ID must start with N or n");
return;

}

}

fetch("http://127.0.0.1:5000/register",{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({
id:id,
name:name,
email:email,
password:password,
role:role
})

})
.then(res=>res.json())
.then(data=>{
alert(data.message);
});

}