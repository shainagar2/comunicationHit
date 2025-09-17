import React, {useState} from "react";
import { useNavigate } from "react-router-dom";
import { loginUser } from "../api/api";

function Login(){
    const navigate = useNavigate();
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [errors, setErrors] = useState({});
    const [serverError, setServerError] = useState(null);
    const [loading, setLoading] = useState(false);

    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_\-+={};':"\\|,.<>/?]).{10,}$/;

    const handleSubmit = async (e) => {
        e.preventDefault();
        let newErrors = {};
        //frontend validation
        if (!username.trim()){
            newErrors.username = "Username is required";
        }
        if (!password){
            newErrors.password = "Password is required";
        }else if (password.length < 10){
            newErrors.password = "Password must be at least 10 characters";
        }else if (!passwordRegex.test(password)){
            newErrors.password = "Password must contain uppercase,lowercase,number,and spacial characters";
        }
        setErrors(newErrors);
        setServerError(null);
        //if frontend validation passed then backend validation, api call
        if (Object.keys(newErrors).length === 0){
            setLoading(true);
            try{
                const data = await loginUser({username,password});
                console.log("Login success:",data);
                localStorage.setItem("token",data.token);
                navigate("/dashboard");
            }catch(err){
                setServerError(err.message);
            }finally{
                setLoading(false);
            }
        }
    };
    return(
        <div style={{maxWidth:'400px', margin:'50px auto', padding:'50px', border:'1px solid #ccc', borderRadius: '8px'}}>
        <h2 style={{textAlign:'center'}}>Login</h2>
        <form onSubmit={handleSubmit}>
           <div style={{marginBottom:'15px', marginRight:'10px'}}>
            <label>Username</label>
            <input type="text" placeholder="Enter username" value={username} onChange={(e)=> setUsername(e.target.value)} style={{width:'100%', padding:'8px'}} />
            {errors.username && (<p style={{ color: "red", fontSize: "12px" }}>{errors.username}</p>)}
           </div> 
           <div style={{marginBottom:'15px', marginRight:'10px'}}>
            <label>Password</label>
            <input type="text" placeholder="Enter password" value={password} onChange={(e)=> setPassword(e.target.value)} style={{width:'100%', padding:'8px'}} />
            {errors.password && (<p style={{ color: "red", fontSize: "12px" }}>{errors.password}</p>)}
           </div> 
           {serverError && (<p style={{ color: "red", fontSize: "12px" }}>{serverError}</p>)}
           <button type="submit" disabled={loading} style={{width:'100%', padding:'10px', backgroundColor:'#3498db', color:'#fff', border:'none', borderRadius:'5px'}}  >
           {loading ? "Logging in..." : "Login"}
           </button>
           <button type="button" onClick={()=> navigate("/register")}>
            Sign Up
            </button>
            <button type="button" onClick={()=> navigate("/forgotpassword")}>
                Forgot Password
            </button>
        </form>
    </div>
    );
}


export default Login;