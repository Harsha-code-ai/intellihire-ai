import { useState } from "react";
import axios from "axios";

const API_URL = "https://intellihire-ai-6.onrender.com";

function App() {

  const [role, setRole] = useState("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [result, setResult] = useState("");

  const [resumeFile, setResumeFile] = useState(null);
  const [resumeResult, setResumeResult] = useState(null);

  const [history, setHistory] = useState([]);

  const [score, setScore] = useState(null);
  const [feedback, setFeedback] = useState("");

  const generateQuestion = async () => {

    const res = await axios.post(
      "http://127.0.0.1:8000/generate-question",
      { role: role }
    );

    setQuestion(res.data.question);
  };

  const evaluateAnswer = async () => {

    const res = await axios.post(
      `${API_URL}/generate-question`,
      { answer: answer }
    );

    setScore(res.data.score);
    setFeedback(res.data.feedback);

    setResult(`Score: ${res.data.score} | Feedback: ${res.data.feedback}`);
  };

  const saveInterview = async () => {

    await axios.post(
      `${API_URL}/save-interview`
      {
        role: role,
        question: question,
        answer: answer,
        score: score,
        feedback: feedback
      }
    );

    alert("Interview saved!");
  };

  const loadHistory = async () => {

    const res = await axios.get(
      `${API_URL}/interview-history`
    );

    setHistory(res.data);
  };

  const analyzeResume = async () => {

    const formData = new FormData();
    formData.append("file", resumeFile);

    const res = await axios.post(
      `${API_URL}/analyze-resume`,
      formData
    );

    setResumeResult(res.data);
  };

  return (

    <div style={{
      fontFamily:"Arial",
      minHeight:"100vh",
      padding:"40px",
      background:"linear-gradient(135deg,#667eea,#764ba2)",
      color:"white"
    }}>

      <h1 style={{textAlign:"center",marginBottom:"40px"}}>
        🚀 IntelliHire AI Interview Platform
      </h1>

      <div style={{
        display:"flex",
        gap:"30px",
        flexWrap:"wrap",
        justifyContent:"center"
      }}>

        {/* Interview Card */}

        <div style={{
          background:"white",
          color:"black",
          padding:"25px",
          width:"420px",
          borderRadius:"12px",
          boxShadow:"0 10px 20px rgba(0,0,0,0.3)",
          transition:"transform 0.3s"
        }}>

          <h2>🎤 Interview Practice</h2>

          <input
            type="text"
            placeholder="Enter Role (Python / Backend)"
            value={role}
            onChange={(e)=>setRole(e.target.value)}
            style={{width:"100%",padding:"10px"}}
          />

          <br/><br/>

          <button onClick={generateQuestion} style={{
            background:"#667eea",
            color:"white",
            border:"none",
            padding:"10px 15px",
            borderRadius:"6px",
            cursor:"pointer"
          }}>
            Generate Question
          </button>

          <p style={{marginTop:"15px"}}><b>Question:</b> {question}</p>

          <textarea
            rows="5"
            style={{width:"100%"}}
            value={answer}
            onChange={(e)=>setAnswer(e.target.value)}
          />

          <br/><br/>

          <button onClick={evaluateAnswer} style={{
            background:"#28a745",
            color:"white",
            border:"none",
            padding:"10px 15px",
            borderRadius:"6px",
            cursor:"pointer"
          }}>
            Evaluate
          </button>

          <button onClick={saveInterview} style={{
            marginLeft:"10px",
            background:"#ff9800",
            color:"white",
            border:"none",
            padding:"10px 15px",
            borderRadius:"6px",
            cursor:"pointer"
          }}>
            Save
          </button>

          <p style={{marginTop:"10px"}}>{result}</p>

        </div>

        {/* Resume Card */}

        <div style={{
          background:"white",
          color:"black",
          padding:"25px",
          width:"420px",
          borderRadius:"12px",
          boxShadow:"0 10px 20px rgba(0,0,0,0.3)"
        }}>

          <h2>📄 Resume Analyzer</h2>

          <input
            type="file"
            onChange={(e)=>setResumeFile(e.target.files[0])}
          />

          <br/><br/>

          <button onClick={analyzeResume} style={{
            background:"#764ba2",
            color:"white",
            border:"none",
            padding:"10px 15px",
            borderRadius:"6px",
            cursor:"pointer"
          }}>
            Analyze Resume
          </button>

          {resumeResult && (

            <div style={{marginTop:"20px"}}>

              <h3>✔ Skills Found</h3>

              <ul>
                {resumeResult.skills_found.map((skill,index)=>(
                  <li key={index}>{skill}</li>
                ))}
              </ul>

              <h3>❌ Missing Skills</h3>

              <ul>
                {resumeResult.missing_skills.map((skill,index)=>(
                  <li key={index}>{skill}</li>
                ))}
              </ul>

              <p><b>Role Match:</b> {resumeResult.role_match_percentage}%</p>

              {/* Progress Bar */}

              <div style={{
                width:"100%",
                height:"18px",
                background:"#ddd",
                borderRadius:"10px"
              }}>

                <div style={{
                  width:`${resumeResult.role_match_percentage}%`,
                  height:"100%",
                  background:"#4CAF50",
                  borderRadius:"10px"
                }}></div>

              </div>

              <p style={{marginTop:"10px"}}>
                💡 {resumeResult.suggestions}
              </p>

            </div>

          )}

        </div>

      </div>

      {/* History */}

      <div style={{
        marginTop:"40px",
        background:"white",
        color:"black",
        padding:"20px",
        borderRadius:"12px"
      }}>

        <h2>📊 Interview History</h2>

        <button onClick={loadHistory} style={{
          background:"#667eea",
          color:"white",
          border:"none",
          padding:"10px 15px",
          borderRadius:"6px"
        }}>
          Load History
        </button>

        {history.map((item)=>(
          <div key={item.id} style={{
            border:"1px solid #ccc",
            padding:"10px",
            margin:"10px",
            borderRadius:"8px"
          }}>

            <p><b>Role:</b> {item.role}</p>
            <p><b>Question:</b> {item.question}</p>
            <p><b>Answer:</b> {item.answer}</p>
            <p><b>Score:</b> {item.score}</p>
            <p><b>Feedback:</b> {item.feedback}</p>

          </div>
        ))}

      </div>

    </div>
  );
}

export default App;
