import React, {useState} from "react";
import { useNavigate } from "react-router-dom";

const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_\-+={};':"\\|,.<>/?]).{10,}$/;

function Register(){
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        username:"",
        email:"",
        password:"",
        confirmPassword:"",
    });
    const [errors, setErrors] = useState({});

    const handleChange = (e)=> {
        setFormData({...formData,[e.target.name]:e.target.value});
    };
    const validate =() => {
        const newErrors = {};

        if (!formData.username || formData.username.length < 2){
            newErrors.username = "Username must be at least 2 characters.";
        }
        if (!formData.email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)){
            newErrors.email = "Enter a valid email address.";
        }
        if (!passwordRegex.test(formData.password)){
            newErrors.password = "Password must be at least 10 characters, include upper/lowercase, and a spacial chararcters";
        }
        if (formData.password !== formData.confirmPassword){
            newErrors.confirmPassword = "Password do not match";
        }
        return newErrors;
    };
    const handleSubmit = (e)=> {
        e.preventDefault();
        const validationErrors = validate();
        if (Object.keys(validationErrors).length > 0){
            setErrors(validationErrors);
        }else {
            setErrors({});
            alert("Registration successeful");
        }
    };
    

    return(
        <div style={{maxWidth:'400px', margin:'50px auto', padding:'50px', border:'1px solid #ccc', borderRadius: '8px'}}>
            <h2 style={{textAlign:'center'}}>Register</h2>
            <form onSubmit={handleSubmit}>
                {/*username*/}
               <div style={{marginBottom:'15px', marginRight:'10px'}}>
                <label>Username</label>
                <input type="text" name="username" placeholder="Enter username" value={formData.username} onChange={handleChange} style={{width:'100%', padding:'8px'}} />
                {errors.username && (<p style={{ color: "red", fontSize: "12px" }}>{errors.username}</p>)}
               </div>
               {/*email*/}
               <div style={{marginBottom:'15px', marginRight:'10px'}}>
                <label>Email</label>
                <input type="text" name="email" placeholder="Enter email" value={formData.email} onChange={handleChange} style={{width:'100%', padding:'8px'}} />
                {errors.email && (<p style={{color: "red", fontSize: "12px"}}>{errors.email}</p>)}
               </div>
               {/*password*/} 
               <div style={{marginBottom:'15px', marginRight:'10px'}}>
                <label>Password</label>
                <input type="password" name="password" placeholder="Enter password" value={formData.password} onChange={handleChange} style={{width:'100%', padding:'8px'}} />
                {errors.password && (<p style={{color: "red", fontSize: "12px"}}>{errors.password}</p>)}
               </div> 
               {/*confirm password*/}
               <div style={{marginBottom:'15px', marginRight:'10px'}}>
                <label>Confirm Password</label>
                <input type="text" name="confirmPassword" placeholder="Confirm password" value={formData.confirmPassword} onChange={handleChange} style={{width:'100%', padding:'8px'}} />
                {errors.confirmPassword && (<p style={{color: "red", fontSize: "12px"}}>{errors.confirmPassword}</p>)}
               </div>
               <button type="submit" style={{width:'100%', padding:'10px', backgroundColor:'#3498db', color:'#fff', border:'none', borderRadius:'5px'}}  >
                Register
               </button>
               <button type="button" onClick={()=> navigate("/Login")} style={{width:'100%', padding:'10px',
                 backgroundColor:'#3498db', color:'#fff', border:'none', borderRadius:'5px',marginTop:'5px'}}  >
                Back to Login
               </button>
            </form>
        </div>
    );
}


export default Register;