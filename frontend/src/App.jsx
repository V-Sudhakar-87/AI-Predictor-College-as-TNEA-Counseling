import { useState, useEffect, useMemo } from 'react'
import heroRobot from './assets/robo.png'
import collegeLogo from './assets/COLLEGE LOGO (1).png'
import { getSeats, SEATS_BY_COLLEGE } from './data/seats.js'
import { useRef } from "react";



const API_URL =
  window.location.hostname === "localhost" ||
  window.location.hostname === "127.0.0.1"
    ? "http://127.0.0.1:8000"
    : "https://ai-predictor-college-as-tnea-counseling.onrender.com";
// ── Branch data with icons ──────────────────────────────────────────────────
const ALL_BRANCHES = [
  { name: 'Computer Science & Engineering (CSE)', icon: <i className="fa-solid fa-computer"></i> },
  { name: 'Artificial Intelligence & Data Science', icon: <i className="fa-solid fa-robot"></i> },
  { name: 'Information Technology', icon: <i className="fa-solid fa-globe"></i>},
  { name: 'Electronics & Communication (ECE)', icon: <i className="fa-solid fa-tower-broadcast"></i> },
  { name: 'Electrical & Electronics (EEE)', icon: <i className="fa-solid fa-bolt"></i> },
  { name: 'Mechanical Engineering', icon: <i className="fa-solid fa-gear"></i> },
  { name: 'Civil Engineering', icon: <i className="fa-solid fa-building"></i> },
  { name: 'Chemical Engineering', icon: <i className="fa-solid fa-flask"></i> },
  { name: 'Biotechnology', icon: <i className="fa-solid fa-microscope"></i> },
  { name: 'Biomedical Engineering', icon: <i className="fa-solid fa-droplet"></i> },
  { name: 'Aerospace Engineering', icon: <i className="fa-solid fa-rocket"></i>},
  { name: 'Automobile Engineering', icon: <i className="fa-solid fa-truck"></i> },
  { name: 'Mechatronics', icon: <i className="fa-solid fa-hand-back-fist"></i> },
  { name: 'Robotics & Automation', icon: <i className="fa-solid fa-robot"></i> },
  { name: 'Cyber Security', icon: <i className="fa-solid fa-lock"></i>},
  { name: 'AI & Machine Learning', icon: <i className="fa-solid fa-brain"></i> },
  { name: 'Data Science', icon: <i className="fa-solid fa-chart-area"></i> },
  { name: 'Other (Specialized)', icon: <i className="fa-solid fa-plus"></i> },
]



// ── Compute cutoff from marks ───────────────────────────────────────────────
function computeCutoff(maths, physics, chemistry) {
  const m = parseFloat(maths)
  const p = parseFloat(physics)
  const c = parseFloat(chemistry)
  if (isNaN(m) && isNaN(p) && isNaN(c)) return null
  const mVal = isNaN(m) ? 0 : Math.min(Math.max(m, 0), 100)
  const pVal = isNaN(p) ? 0 : Math.min(Math.max(p, 0), 100)
  const cVal = isNaN(c) ? 0 : Math.min(Math.max(c, 0), 100)
  return (mVal + pVal / 2 + cVal / 2)
}

// ── Navbar ──────────────────────────────────────────────────────────────────
function Navbar({ onPredictClick }) {
  return (
    <nav className="navbar" role="navigation" aria-label="Main navigation">
      <a href="#" className="navbar-logo" aria-label="AI College Predictor home">
        <div className="navbar-logo-icon">
           <img src={collegeLogo} alt="College Logo" />
        </div>
        <div className="navbar-brand">
          <span className="navbar-title">AI College Predictor</span>
          <span className="navbar-tagline">Powered by 5 Years of Counselling Data</span>
        </div>
      </a>
    {/* <ul className="navbar-nav">
        <li><a href="#hero" className="active">Home</a></li>
        <li><a href="#features">Features</a></li>
        <li><a href="#how-it-works">How It Works</a></li>
        <li><a href="#predict">Predict</a></li>
      </ul>*/}
      <button className="navbar-cta" id="navbar-predict-btn" onClick={onPredictClick}>
        Predict Now
      </button>
    </nav>
  )
}

// ── Hero Section ─────────────────────────────────────────────────────────────
function HeroSection({ onGetStarted }) {
  return (
    <section className="hero" id="hero" aria-labelledby="hero-heading">
      <div className="hero-content">
        {/* Left */}
        <div className="hero-left">
          <div className="hero-trust-badge" role="status">
            <span className="badge-dot" aria-hidden="true"></span>
            Trusted by 10,000+ Students
          </div>

          <h1 className="hero-heading" id="hero-heading">
            Predict Your<br />
            Dream College<br />
            with <span className="highlight">AI</span>
          </h1>

          <p className="hero-subtext">
            Get accurate college &amp; branch predictions based on 5 years of counselling data,
            community-wise closing ranks &amp; AI analysis.
          </p>

          <div className="hero-actions desktop-btn">
            <button
              className="btn-primary"
              id="hero-get-started-btn"
               onClick={() =>
               document.getElementById("features")?.scrollIntoView({
               behavior: "smooth",
              block: "start"
              })
              }
              aria-label="Get started with prediction"
              >
              Get Started →
            </button>
            {/*<button
              className="btn-secondary"
              id="hero-explore-btn"
              onClick={() => document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' })}
              aria-label="Explore features"
            >
              Explore Features ▶
            </button>*/}
          </div>
        </div>

        {/* Right */}
        <div className="hero-right" aria-hidden="true">
          {/* Floating stat cards */}
          <div className="hero-stat-card stat-card-top-left">
            <div className="stat-card-icon">🛡️</div>
            <div>
              <div className="stat-card-value">5</div>
              <div className="stat-card-label">Years of Data</div>
            </div>
          </div>

          <div className="hero-stat-card stat-card-top-right">
            <div className="stat-card-icon">⚙️</div>
            <div>
              <div className="stat-card-value">100K+</div>
              <div className="stat-card-label">Predictions Made</div>
            </div>
          </div>

          <div className="hero-stat-card stat-card-bottom-right">
            <div className="stat-card-icon"><i className="fa-solid fa-graduation-cap" style={{color:'white'}}></i></div>
            <div>
              <div className="stat-card-value">95%</div>
              <div className="stat-card-label">Accuracy Rate</div>
            </div>
          </div>

          <img
            src={heroRobot}
            alt="AI robot assistant analyzing college data"
            className="hero-image"
          />
        </div>
        <div className="hero-actions mobile-btn">
            <button
              className="btn-primary"
              id="hero-get-started-btn"
               onClick={() =>
              document.getElementById("features")?.scrollIntoView({
              behavior: "smooth",
               block: "start"
              })
              }  
              aria-label="Get started with prediction"
             >
              Get Started →
            </button>
   </div>
      </div>
    </section>
  )
}

// ── Features Section ─────────────────────────────────────────────────────────
const FEATURES = [
  {
    icon: <i className="fa-solid fa-arrow-trend-up"></i>,
    color: '#e8f5e9',
    title: 'AI College Prediction',
    desc: 'Predict the best colleges you can get based on your rank & community.',
  },
  {
    icon: <i className="fa-solid fa-ranking-star"></i>,
    color: '#fff8e1',
    title: 'Branch Prediction',
    desc: 'Find the best branches available for your rank in top colleges.',
  },
  {
    icon: <i className="fa-solid fa-arrow-trend-down"></i>,
    color: '#f3e5f5',
    title: 'Closing Rank Trends',
    desc: 'Explore 5 years of closing rank trends for every college.',
  },
  {
    icon: <i className="fa-solid fa-graduation-cap"></i>,
    color: '#e0f7fa',
    title: 'Admission Chance',
    desc: 'Get your admission probability with AI accuracy.',
  },
  {
    icon: <i className="fa-solid fa-scale-balanced"></i>,
    color: '#fce4ec',
    title: 'Compare Colleges',
    desc: 'Compare colleges, branches, fees & placements side by side.',
  },
]

function FeaturesSection() {
  return (
    <section className="features-section" id="features" aria-labelledby="features-heading">
      <div className="section-inner">
        <header className="section-header">
          <h2 id="features-heading">What You Can Do</h2>
          <p>Everything you need for smart admission decisions</p>
        </header>

        <div className="features-grid" role="list">
          {FEATURES.map((f, i) => (
            <article
              key={i}
              className="feature-card"
              role="listitem"
              tabIndex="0"
              aria-label={f.title}
            >
              <div className="feature-icon-wrap" style={{ background: f.color }}>
                {f.icon}
              </div>
              <div className="feature-content">
              <h3>{f.title}</h3>
              <p>{f.desc}</p>
              </div>
            </article>
          ))}
        </div>
        <div className="features-next-btn">
        <button
        className="btn-next"
        onClick={() =>
        document.getElementById("how-it-works")?.scrollIntoView({
        behavior: "smooth",
        block: "start"
        })
        }
        style={{display:'block',fontSize:'18px'}}>
        Next →
        </button>
      </div>
      </div>
    </section>
  )
}

// ── How It Works ─────────────────────────────────────────────────────────────
const HOW_STEPS = [
  { num: '01', icon: '✏️', title: 'Enter Your Details', desc: 'Provide your rank, community & other required details.' },
  { num: '02', icon: '🗄️', title: 'AI Analyzes Data', desc: 'Our AI analyzes 5 years of counselling data & closing ranks.' },
  { num: '03', icon: '📊', title: 'Prediction Generated', desc: 'AI generates the best colleges, branches & admission chances.' },
  { num: '04', icon: '📋', title: 'View Detailed Report', desc: 'Explore detailed report, compare colleges & make smart decisions.' },
]

function HowItWorksSection({ onNext }) {
  return (
    <section className="how-section" id="how-it-works" aria-labelledby="how-heading">
      <div className="section-inner">
        <header className="section-header">
          <h2 id="how-heading">How It Works</h2>
          <p>Simple 4 steps to get your prediction</p>
        </header>

        <div className="how-steps" role="list">
          {HOW_STEPS.map((step, i) => (
            <div key={i} className="how-step" role="listitem" tabIndex="0">
              <div className="how-icon-wrap" aria-hidden="true">{step.icon}</div>
              <div className="how-text">
              <p className="how-step-num">{step.num}</p>
              <h3>{step.title}</h3>
              <p>{step.desc}</p>
              </div>
            </div>
          ))}
        </div>
        <div className="features-next-btn">
        <button
        className="btn-next"
        onClick={onNext}
        style={{display:'block',fontSize:'18px'}}>
        Start Prediction →
        </button>
      </div>
      </div>
    </section>
  )
}

// ── Form Section ─────────────────────────────────────────────────────────────
function PredictorForm({ onResults, onLoading, isLoading, communities, districts, metaLoading, metaError,onClose,savedFormData,
  setSavedFormData }) {
  // Personal Info
  const [fullName, setFullName] = useState('')
  const [district, setDistrict] = useState('')
  const [rankInput, setRankInput] = useState('')
  const [community, setCommunity] = useState('OC')
  const [gender, setGender] = useState('')

  // Academic Info
  const [maths, setMaths] = useState('')
  const [physics, setPhysics] = useState('')
  const [chemistry, setChemistry] = useState('')

  // Branches
  const [branchSearch, setBranchSearch] = useState('')
  const [selectedBranches, setSelectedBranches] = useState([])

  // Validation
  const [validationError, setValidationError] = useState('')

  const [activeStep, setActiveStep] = useState(1);
  const personalRef = useRef(null);
  const academicRef = useRef(null);
  const branchRef = useRef(null);
  const submitRef = useRef(null);
  const formContentRef = useRef(null);

  const [mobileStep, setMobileStep] = useState(1);
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);

useEffect(() => {
  const handleResize = () => setIsMobile(window.innerWidth <= 768);

  window.addEventListener("resize", handleResize);

  return () => window.removeEventListener("resize", handleResize);
}, []);

  const cutoff = useMemo(() => computeCutoff(maths, physics, chemistry), [maths, physics, chemistry])

  const filteredBranches = useMemo(() =>
    ALL_BRANCHES.filter(b =>
      b.name.toLowerCase().includes(branchSearch.toLowerCase())
    ), [branchSearch])

    useEffect(() => {

      function handleScroll(){

          const form = formContentRef.current;

          if(!form) return;

          const y = form.scrollTop;

          if(submitRef.current && y >= submitRef.current.offsetTop - 200){

              setActiveStep(4);

          }else if(branchRef.current && y >= branchRef.current.offsetTop - 200){

              setActiveStep(3);

          }else if(academicRef.current && y >= academicRef.current.offsetTop - 200){

              setActiveStep(2);

          }else{

              setActiveStep(1);

          }

      }

      const form = formContentRef.current;

      if(form){

          form.addEventListener("scroll",handleScroll);

      }

      return ()=>{

          if(form){

              form.removeEventListener("scroll",handleScroll);

          }

      };

  }, []);

  function toggleBranch(name) {
    setSelectedBranches(prev =>
      prev.includes(name) ? prev.filter(b => b !== name) : [...prev, name]
    )
  }

  useEffect(() => { setValidationError('') }, [rankInput, cutoff, community, district])
  useEffect(() => {

    if(!savedFormData) return;

    setFullName(savedFormData.fullName || "");

    setDistrict(savedFormData.district || "");

    setRankInput(savedFormData.rankInput || "");

    setCommunity(savedFormData.community || "OC");

    setGender(savedFormData.gender || "");

    setMaths(savedFormData.maths || "");

    setPhysics(savedFormData.physics || "");

    setChemistry(savedFormData.chemistry || "");

    setSelectedBranches(savedFormData.selectedBranches || []);

}, [savedFormData]);


  async function handleSubmit(e) {
    e.preventDefault()
    setValidationError('')

    const rank = rankInput.trim() ? parseInt(rankInput, 10) : null
    const cutoffMark = cutoff

    if (rank === null && cutoffMark === null) {
      setValidationError('Please enter your Rank List Number or subject marks to proceed.')
      return
    }

    if (rank !== null && (isNaN(rank) || rank <= 0)) {
      setValidationError('Please enter a valid positive rank number.')
      return
    }

    if (cutoffMark !== null && (cutoffMark < 0 || cutoffMark > 200)) {
      setValidationError('Cutoff mark must be between 0 and 200.')
      return
    }

    onLoading(true)

    try {
      const payload = {
        rank: rank,
        cutoff_mark: cutoffMark,
        community: community,
        district: district || null,
      }

      const res = await fetch('${API_URL}/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}))
        throw new Error(errData.detail || `Prediction failed: ${res.statusText}`)
      }

      const data = await res.json()
      let recs = data.recommendations || []
      setSavedFormData({

    fullName,

    district,

    rankInput,

    community,

    gender,

    maths,

    physics,

    chemistry,

    selectedBranches

});

const formValues = {
    fullName,
    district,
    rankInput,
    community,
    gender,
    maths,
    physics,
    chemistry,
    selectedBranches
};

setSavedFormData(formValues);

sessionStorage.setItem(
    "savedFormData",
    JSON.stringify(formValues)
);
      // Client-side filter: keep only branches that fuzzy-match any selected preference
      // Backend branch names e.g. "Computer Science and Engineering", "Information Technology"
      // UI chip names e.g.  "Computer Science & Engineering (CSE)", "Information Technology"
      // Strategy: extract significant words from each chip name and check if the backend branch contains them
      if (selectedBranches.length > 0) {
        // Build a list of keyword sets from selected branch chips
        const chipKeywords = selectedBranches.map(chipName => {
          // Remove parenthetical codes, lower-case, split on non-alpha
          const clean = chipName
            .replace(/\(.*?\)/g, '')      // remove (CSE), (ECE) etc.
            .replace(/&/g, 'and')
            .toLowerCase()
            .split(/[^a-z0-9]+/)
            .filter(w => w.length > 2 && !['and', 'the', 'for', 'with'].includes(w))
          return clean
        })

        recs = recs
          .map(rec => ({
            ...rec,
            branches: rec.branches.filter(backendBranch => {
              const bl = backendBranch.toLowerCase().replace(/&/g, 'and')
              // A branch matches a chip if ALL significant words of the chip appear in the branch string
              return chipKeywords.some(keywords =>
                keywords.every(kw => bl.includes(kw))
              )
            }),
          }))
          .filter(rec => rec.branches.length > 0)
      }

      onResults(recs, null, {
        fullName,
        rank: rank,
        cutoffMark: cutoffMark,
        community,
        district: district || 'All Districts',
        branches: selectedBranches,
        totalFromApi: data.recommendations?.length || 0,
      })
    } catch (err) {
      console.error('Prediction error:', err)
      onResults([], err.message || 'An unexpected error occurred.', null)
    } finally {
      onLoading(false)
    }
  }

  return (
    <section className="form-section" id="predict" aria-labelledby="form-heading">
      <form
        className="form-container"
        onSubmit={handleSubmit}
        aria-labelledby="form-heading"
        noValidate
      >
        <div className="form-sidebar">

<div className="sidebar-top">

    <div className="sidebar-logo">
        🤖
    </div>

    <h2>AI College Predictor</h2>


</div>

<div className="sidebar-steps">

<div className={`step ${activeStep===1 ? "active":""}`}>

<span>01</span>

Personal Information

</div>

<div className={`step ${activeStep===2 ? "active":""}`}>

<span>02</span>

Academic Details

</div>

<div className={`step ${activeStep===3 ? "active":""}`}>

<span>03</span>

Preferred Branches

</div>

<div className={`step ${activeStep===4 ? "active":""}`}>

<span>04</span>

Generate Report

</div>

</div>

<div className="sidebar-bottom">


<button
type="button"
className="close-modal-btn"
onClick={onClose}
>

Cancel

</button>

</div>
</div>

<div className="form-content" ref={formContentRef}>

  


        {/* Form Header */}
        <header className="form-header">
         {/*<span className="form-header-art" aria-hidden="true">📋</span>*/}
          <h1 id="form-heading">
            Enter <span className="form-heading-accent">Your</span> Details
          </h1>
          <p>Fill in the details below to get accurate college predictions</p>

          <button className="modal-close" type="button" onClick={onClose}>✕</button>

          <div className="privacy-notice" role="note" aria-label="Privacy notice">
            <span className="privacy-notice-icon"><i className="fa-solid fa-shield-halved fa-2x" style={{marginTop:'10px',marginLeft:'7px'}} ></i></span>
            <div>
              <strong>Your data is safe with us</strong>
              <span>We never share your personal information</span>
            </div>
          </div>
        </header>

        {/* Validation Error */}
        {validationError && (
          <div className="form-validation-alert" role="alert" aria-live="polite">
            ⚠️ {validationError}
          </div>
        )}

        {/* 1. Personal Information */}
        {(!isMobile || mobileStep === 1) && (
        <fieldset className="form-block" ref={personalRef}>
          <div className="form-block-header">
            <div className="form-block-num" aria-hidden="true">1</div>
            <legend>
              <h2>Personal Information</h2>
            </legend>
          </div>

          <div className="form-row" style={{ gridTemplateColumns: 'repeat(5, 1fr)', alignItems: 'end' }}>
            {/* Full Name */}
            <div className="form-col">
              <label htmlFor="full-name">Full Name</label>
              <div className="field-wrap">
                <span className="field-icon" aria-hidden="true"><i className="fa-solid fa-user"></i></span>
                <input
                  type="text"
                  id="full-name"
                  className="field-input"
                  placeholder="Enter your full name"
                  value={fullName}
                  onChange={e => setFullName(e.target.value)}
                  autoComplete="name"
                />
              </div>
            </div>

            {/* District */}
            <div className="form-col">
              <label htmlFor="district-select">
                Preferred District Colleges <span className="req" aria-hidden="true">*</span>
              </label>
              <div className="field-wrap">
                <span className="field-icon" aria-hidden="true"><i className="fa-solid fa-location-dot"></i></span>
                {metaLoading ? (
                  <select className="field-input" disabled aria-busy="true">
                    <option>Loading...</option>
                  </select>
                ) : (
                  <select
                    id="district-select"
                    className="field-input"
                    value={district}
                    onChange={e => setDistrict(e.target.value)}
                  >
                    <option value="">All Districts</option>
                    {districts.map(d => (
                      <option key={d} value={d}>{d}</option>
                    ))}
                  </select>
                )}
              </div>
            </div>

            {/* Rank */}
            <div className="form-col">
              <label htmlFor="rank-input">
                Rank List Number <span className="req" aria-hidden="true">*</span>
              </label>
              <div className="field-wrap">
                <span className="field-icon" aria-hidden="true">#</span>
                <input
                  type="text"
                  inputMode="numeric"
                  id="rank-input"
                  className="field-input"
                  placeholder="e.g. 1500"
                  value={rankInput}
                  onChange={e => setRankInput(e.target.value.replace(/[^0-9]/g, ''))}
                  autoComplete="off"
                />
              </div>
            </div>

            {/* Community */}
            <div className="form-col">
              <label htmlFor="community-select">
                Community <span className="req" aria-hidden="true">*</span>
              </label>
              <div className="field-wrap">
                <span className="field-icon" aria-hidden="true">👥</span>
                <select
                  id="community-select"
                  className="field-input"
                  value={community}
                  onChange={e => setCommunity(e.target.value)}
                >
                  {communities.map(c => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Gender */}
            <div className="form-col">
              <label htmlFor="gender-select">Gender</label>
              <div className="field-wrap">
                <span className="field-icon" aria-hidden="true">⚧</span>
                <select
                  id="gender-select"
                  className="field-input"
                  value={gender}
                  onChange={e => setGender(e.target.value)}
                >
                  <option value="">Select gender</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </div>
          </div>
          {isMobile && (
  <div className="mobile-nav">
    <button
      type="button"
      className="btn-next"
      onClick={() => setMobileStep(2)}
    style={{marginLeft:'60px'}}>
      Next →
    </button>
  </div>
)}
        </fieldset>
)}
        {/* 2. Academic Information */}
        {(!isMobile || mobileStep === 2) && (
        <fieldset className="form-block" ref={academicRef}>
          <div className="form-block-header">
            <div className="form-block-num" aria-hidden="true">2</div>
            <legend><h2>Academic Information</h2></legend>
          </div>

          <div className="academic-grid">
            {/* Maths */}
            <div className="form-col">
              <label htmlFor="maths-mark">
                Maths Mark (Max 100) <span className="req" aria-hidden="true">*</span>
              </label>
              <div className="field-wrap">
                <span className="field-icon" aria-hidden="true">#</span>
                <input
                  type="text"
                  inputMode="decimal"
                  id="maths-mark"
                  className="field-input"
                  placeholder="e.g. 95"
                  value={maths}
                  onChange={e => setMaths(e.target.value.replace(/[^0-9.]/g, ''))}
                  autoComplete="off"
                />
              </div>
            </div>

            {/* Physics */}
            <div className="form-col">
              <label htmlFor="physics-mark">
                Physics Mark (Max 100) <span className="req" aria-hidden="true">*</span>
              </label>
              <div className="field-wrap">
                <span className="field-icon" aria-hidden="true">#</span>
                <input
                  type="text"
                  inputMode="decimal"
                  id="physics-mark"
                  className="field-input"
                  placeholder="e.g. 85"
                  value={physics}
                  onChange={e => setPhysics(e.target.value.replace(/[^0-9.]/g, ''))}
                  autoComplete="off"
                />
              </div>
            </div>

            {/* Chemistry */}
            <div className="form-col">
              <label htmlFor="chemistry-mark">
                Chemistry Mark (Max 100) <span className="req" aria-hidden="true">*</span>
              </label>
              <div className="field-wrap">
                <span className="field-icon" aria-hidden="true">#</span>
                <input
                  type="text"
                  inputMode="decimal"
                  id="chemistry-mark"
                  className="field-input"
                  placeholder="e.g. 85"
                  value={chemistry}
                  onChange={e => setChemistry(e.target.value.replace(/[^0-9.]/g, ''))}
                  autoComplete="off"
                />
              </div>
            </div>

            {/* Cutoff auto display */}
            <div className="form-col">
              <div className="cutoff-label-right">
                <label>Engineering Cutoff</label>
                <span className="cutoff-auto-tag">Auto Calculated</span>
              </div>
              <div className="cutoff-display" aria-live="polite" aria-label={`Engineering cutoff: ${cutoff !== null ? cutoff.toFixed(2) : 'not calculated'} out of 200`}>
                <div className="cutoff-display-value">
                  {cutoff !== null ? cutoff.toFixed(2) : '--'} <span style={{ fontSize: '0.7rem', fontWeight: 400, color: 'var(--text-light)' }}>/ 200</span>
                </div>
                <div className="cutoff-display-note">Will be calculated automatically</div>
              </div>
            </div>
          </div>
          {isMobile && (
  <div className="mobile-nav">

    <button
      type="button"
      className="btn-next"
      onClick={() => setMobileStep(1)}
    >
      ← Back
    </button>

    <button
      type="button"
      className="btn-next"
      onClick={() => setMobileStep(3)}
    style={{marginLeft:'50px'}}>
      Next →
    </button>

  </div>
)}
        </fieldset>
)}
        {/* 3. Preferred Branches */}
        {(!isMobile || mobileStep === 3) && (
        <fieldset className="form-block" ref={branchRef}>
          <div className="form-block-header">
            <div className="form-block-num" aria-hidden="true">3</div>
            <legend>
              <h2>Preferred Branches <span className="form-block-sub">(Select one or more)</span></h2>
            </legend>
          </div>

          {/* Branch Search */}
          <div className="branch-search-wrap" role="search" >
            <span className="branch-search-icon" aria-hidden="true">
              <i className="fa-solid fa-magnifying-glass"></i>
              </span>
            <input
              type="search"
              id="branch-search"
              className="branch-search-input"
              placeholder="Search branch..."
              value={branchSearch}
              onChange={e => setBranchSearch(e.target.value)}
              aria-label="Search branches"
            />
          </div>

          <div className="branches-grid" role="group" aria-label="Branch selection">
            {filteredBranches.map(branch => {
              const isSelected = selectedBranches.includes(branch.name)
              return (
                <button
                  key={branch.name}
                  type="button"
                  className={`branch-chip${isSelected ? ' selected' : ''}`}
                  onClick={() => toggleBranch(branch.name)}
                  aria-pressed={isSelected}
                  id={`branch-${branch.name.replace(/\s+/g, '-').replace(/[^a-zA-Z0-9-]/g, '')}`}
                >
                  <span className="branch-chip-icon" aria-hidden="true">{branch.icon}</span>
                  <span style={{ flex: 1, textAlign: 'left', lineHeight: 1.3 }}>{branch.name}</span>
                  <span className="chip-check" aria-hidden="true">{isSelected ? '✓' : ''}</span>
                </button>
              )
            })}
          </div>
          <div className="mobile-nav">
    <button
      type="button"
      className="btn-next"
      onClick={() => setMobileStep(2)}
     style={{marginLeft:'50px'}} >
      ← Back
    </button>
  </div>
        </fieldset>
)}
        {/* Submit */}
        {(!isMobile || mobileStep === 3) && (
        <div className="form-submit-wrap" ref={submitRef}>
          <button
            type="submit"
            className="btn-generate"
            id="generate-prediction-btn"
            disabled={isLoading}
            aria-label="Generate AI prediction"
          >
            {isLoading ? (
              <>
                <span className="spinner" style={{ width: '22px', height: '22px', borderWidth: '2px' }} aria-hidden="true"></span>
                Analyzing your profile...
              </>
            ) : (
              <>✨ Generate AI Prediction →</>
            )}
          </button>
          <p className="btn-generate-note">
            Our AI will analyze 5 years of counselling data to find the best colleges for you
          </p>
        </div>
)}
        {metaError && (
          <div className="form-validation-alert" role="alert" style={{ marginTop: '16px' }}>
            ⚠️ {metaError}
          </div>
        )}
        </div>
      </form>
    </section>
  )
}

// ── Results Section ──────────────────────────────────────────────────────────
function ResultsSection({ recommendations, error, hasSearched, isLoading, onRetry, debugInfo, openHostel, hostelData,
    showHostel,
    setShowHostel ,openWebsite,downloadPDF}) {
  const [searchQuery, setSearchQuery] = useState('')
  const [expandedColleges, setExpandedColleges] = useState({})

  const filtered = useMemo(() => {
    const q = searchQuery.toLowerCase().trim()
    if (!q) return recommendations
    return recommendations.filter(rec =>
      rec.college.toLowerCase().includes(q) ||
      rec.branches.some(b => b.toLowerCase().includes(q))
    )
  }, [recommendations, searchQuery])

  function toggleExpand(name) {
    setExpandedColleges(prev => ({ ...prev, [name]: !prev[name] }))
  }

  if (!hasSearched && !isLoading) return null

  if (isLoading) {
    return (
      <section className="results-section" aria-label="Loading results" aria-live="polite">
        <div className="results-inner">
          <div className="spinner-wrap">
            <div className="spinner" role="status" aria-label="Loading"></div>
            <h3>Analyzing admission criteria...</h3>
            <p>Predicting rank targets and cutoff requirements across historical distributions.</p>
          </div>
        </div>
      </section>
    )
  }

  if (error) {
    return (
      
      <section className="results-section" aria-label="Prediction error" aria-live="assertive">
        <div className="results-inner">
          <div className="error-state">
            <div className="error-icon">❌</div>
            <h3>Prediction Error</h3>
            <p>{error}</p>
            <button className="btn-primary" onClick={onRetry} style={{ marginTop: '20px' }}>
              Try Again
            </button>
          </div>
        </div>
      </section>
    )
  }

  if (recommendations.length === 0) {
    const filteredByBranch = debugInfo && debugInfo.branches?.length > 0 && debugInfo.totalFromApi > 0
    return (
      <section className="results-section" aria-label="No results found" aria-live="polite">
        <div className="results-inner">
          <div className="empty-state">
            <div className="empty-icon">{filteredByBranch ? '🌿' : '🔍'}</div>
            <h3>{filteredByBranch ? 'No Matching Branches' : 'No Colleges Found'}</h3>
            {filteredByBranch ? (
              <p>
                The AI found <strong>{debugInfo.totalFromApi} colleges</strong> for your rank/community,
                but none offered the branch(es) you selected. Try deselecting some branches
                or leave all branches unselected to see all available options.
              </p>
            ) : (
              <p>
                No historically feasible colleges found for your inputs. Try:
                <br /><br />
                • Removing the district filter (set to All Districts)<br />
                • Using a higher rank number (e.g. 5000, 10000)<br />
                • Entering only rank <em>or</em> only marks (not both together)<br />
                • Selecting a different community
              </p>
            )}
            {debugInfo && (
              <div style={{ marginTop: '18px', background: 'var(--cream)', borderRadius: '10px', padding: '12px 16px', textAlign: 'left', fontSize: '0.8rem', color: 'var(--text-muted)', border: '1px solid var(--cream-border)' }}>
                <strong style={{ color: 'var(--text-mid)', display: 'block', marginBottom: '4px' }}>Search Parameters Sent:</strong>
                {debugInfo.rank && <span>Rank: <b>{debugInfo.rank}</b> &nbsp;</span>}
                {debugInfo.cutoffMark !== null && <span>Cutoff: <b>{debugInfo.cutoffMark?.toFixed(2)}</b> &nbsp;</span>}
                <span>Community: <b>{debugInfo.community}</b> &nbsp;</span>
                <span>District: <b>{debugInfo.district}</b></span>
                {debugInfo.branches?.length > 0 && <div style={{ marginTop: '4px' }}>Branches: <b>{debugInfo.branches.join(', ')}</b></div>}
              </div>
            )}
            <button
              className="btn-primary"
              onClick={onRetry}
              style={{ marginTop: '20px', fontSize: '0.9rem', padding: '12px 24px' }}
            >
              ← Modify Search
            </button>
          </div>
        </div>
      </section>
    )
  }

  return (
    <section className="results-section" aria-labelledby="results-heading" aria-live="polite">
      <div className="results-inner">
        <div className="results-header">
          <div className="results-heading">
            <h2 id="results-heading">✨ AI Predicted Best-Fit Colleges</h2>
            <span className="results-count-badge" aria-label={`${filtered.length} colleges found`}>
              {filtered.length} Found
            </span>
          </div>

          <div className="results-search" role="search">
            <span aria-hidden="true"><i className="fa-solid fa-magnifying-glass"></i></span>
            <input
              type="search"
              placeholder="Filter by college or branch…"
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              aria-label="Search results"
              id="results-search-input"
            />
          </div>
        </div>

        {filtered.length === 0 && searchQuery ? (
          <div className="empty-state" style={{ marginTop: 0 }}>
            <div className="empty-icon"><i className="fa-solid fa-magnifying-glass"></i></div>
            <h3>No Matches</h3>
            <p>No results match &ldquo;{searchQuery}&rdquo;. Try clearing the filter.</p>
            <button className="btn-primary" onClick={() => setSearchQuery('')} style={{ marginTop: '16px' }}>
              Clear Filter
            </button>
          </div>
        ) : (
          <div className="results-grid">
            {[...filtered].reverse().map((rec) => {
              const isExpanded = expandedColleges[rec.college] || false
              const displayedBranches = isExpanded ? rec.branches : rec.branches.slice(0, 4)
              const hasMore = rec.branches.length > 4

              return (
                <article
                  key={`${rec.code}-${rec.college}`}
                  className="college-card"
                  aria-label={`${rec.college}, ${rec.district}`}
                >
                  <div className="college-card-top">
                    <h3 className="college-card-name">{rec.college}</h3>
                    <span className="college-card-code" aria-label={`College code ${rec.code}`}>
                      CODE: {rec.code}
                    </span>
                  </div>
                <div className="footer-top">
                  <div className="college-card-district" aria-label={`District: ${rec.district}`}>
                    <i className="fa-solid fa-location-dot"></i> {rec.district}
                  </div>
                  <button className="hostel-badge" onClick={() => openHostel(rec.code)}>
                   <i className="fa-solid fa-hotel"></i>Hostel & Fees
                   </button>
                  <button className="website-btn" onClick={() => openWebsite(rec.code)}>
                  <i className="fa-solid fa-globe"></i> Website</button>
                  </div>
                 
                  <div>
                    <p className="branches-header">
                      Feasible Branches ({rec.branches.length})
                    </p>
                    <div className="branches-list" role="list">
                      {displayedBranches.map((branch, idx) => {
                        const seats = getSeats(rec.code, branch)
                        const isConfirmed = !!SEATS_BY_COLLEGE[String(rec.code)]
                        return (
                          <div key={idx} className="branch-item" role="listitem">
                            <span className="branch-item-name">{branch}</span>
                            <span
                              className={`branch-seat-badge${isConfirmed ? ' confirmed' : ' estimated'}`}
                              title={isConfirmed
                                ? `Seat intake from 5-year TNEA dataset (AICTE approved)`
                                : `Estimated intake — exact data coming after counselling`}
                            >
                              🪑 {seats} seats
                              {!isConfirmed && <span className="seat-est-mark">~</span>}
                            </span>
                          </div>
                        )
                      })}
                    </div>

                    {hasMore && (
                      <button
                        className="show-more-btn"
                        onClick={() => toggleExpand(rec.college)}
                        aria-expanded={isExpanded}
                        aria-label={isExpanded ? 'Show fewer branches' : `Show ${rec.branches.length - 4} more branches`}
                      >
                        {isExpanded
                          ? 'Show Less ▴'
                          : `Show ${rec.branches.length - 4} More Branches ▾`}
                      </button>
                    )}
                  </div>
                </article>
              )
            })}
          </div>
        )}
      </div>
    </section>
  )
}

// ── App Root ─────────────────────────────────────────────────────────────────
function App() {
  const [communities, setCommunities] = useState(['OC', 'BC', 'BCM', 'MBC', 'SC', 'SCA', 'ST'])
  const [districts, setDistricts] = useState([])
  const [metaLoading, setMetaLoading] = useState(true)
  const [metaError, setMetaError] = useState(null)

  const [recommendations, setRecommendations] = useState([])
  const [error, setError] = useState(null)
  const [hostelData, setHostelData] = useState(null);
  const [showHostel, setShowHostel] = useState(false);
  const [hasSearched, setHasSearched] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [debugInfo, setDebugInfo] = useState(null)
  const [showPredictor, setShowPredictor] = useState(false);
  const [previousPage, setPreviousPage] = useState("home");
  const [downloading, setDownloading] = useState(false);
  const [savedFormData, setSavedFormData] = useState(() => {

    const saved = sessionStorage.getItem("savedFormData");

    return saved ? JSON.parse(saved) : null;

});
  const [currentPage, setCurrentPage] = useState(() => {
  return sessionStorage.getItem("currentPage") || "home";
});
useEffect(() => {
  sessionStorage.setItem("currentPage", currentPage);
}, [currentPage]);


  useEffect(() => {
    async function fetchMeta() {
      try {
        setMetaLoading(true)
        const res = await fetch('${API_URL}/api/metadata')
        if (!res.ok) throw new Error(`Failed: ${res.statusText}`)
        const data = await res.json()
        if (data.districts) setDistricts(data.districts)
        if (data.communities) setCommunities(data.communities)
        setMetaError(null)
      } catch (err) {
        console.error('Metadata fetch error:', err)
        setMetaError('Could not load district list. Backend may not be running.')
      } finally {
        setMetaLoading(false)
      }
    }
    fetchMeta()
  }, [])

useEffect(() => {

    const saved = sessionStorage.getItem("dashboardData");

    if (!saved) return;

    const data = JSON.parse(saved);

    setRecommendations(data.recommendations || []);
    setDebugInfo(data.debugInfo || null);

    if (data.recommendations?.length) {
        setHasSearched(true);
    }

}, []);

useEffect(() => {

    if(savedFormData){

        sessionStorage.setItem(
            "savedFormData",
            JSON.stringify(savedFormData)
        );

    }

}, [savedFormData]);

  function handleResults(recs, err, info) {
    setRecommendations(recs)
    setError(err)
    setDebugInfo(info)
    setHasSearched(true)
    
     sessionStorage.setItem(
        "dashboardData",
        JSON.stringify({
            recommendations: recs,
            debugInfo: info
        })
        
    );
    if (!err) {
    setShowPredictor(false);
    setCurrentPage("dashboard");
    
}
  }

  function handleLoading(loading) {
    setIsLoading(loading)
    if (loading) {
      setHasSearched(true)
      setTimeout(() => {
        document.getElementById('results-section-anchor')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }, 100)
    }
  }

  function scrollToPredict() {
    document.getElementById('predict')?.scrollIntoView({ behavior: 'smooth' })
  }
 function openPredictor() {
  setPreviousPage(currentPage);
setShowPredictor(true);
}

function closePredictor() {
  setShowPredictor(false);

}
async function openHostel(collegeCode) {



    const res = await fetch(`${API_URL}/api/college-details/${collegeCode}`);

    const data = await res.json();

    if (data.success) {

        setHostelData(data.data);

        setShowHostel(true);

    }

}
const openWebsite = async (collegeCode) => {

    try {

        const res = await fetch(`${API_URL}/api/college-details/${collegeCode}`);

        const data = await res.json();
       

        if (data.success && data.data.website) {
          let url = data.data.website;

        if(!url.startsWith("http")){

            url = "https://" + url;

        }

        window.open(url,"_blank");
        }

    } catch (err) {
        console.error(err);
    }

};

const downloadPDF = async () => {
if (downloading) return;

    setDownloading(true);

    try {
   const student = {

    name: savedFormData?.fullName || "",

    gender: savedFormData?.gender || "",

    community: savedFormData?.community || "",

    district: savedFormData?.district || "",

    rank: Number(savedFormData?.rankInput || 0),

    maths: Number(savedFormData?.maths || 0),

    physics: Number(savedFormData?.physics || 0),

    chemistry: Number(savedFormData?.chemistry || 0),

    cutoff: debugInfo?.cutoffMark || 0,

    preferredBranches: savedFormData?.selectedBranches || []

};

     const response = await fetch(
            "${API_URL}/api/download-pdf",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    student,
                    recommendations
                })
            }
        );

        const blob = await response.blob();

        const url = window.URL.createObjectURL(blob);

        const a = document.createElement("a");

        a.href = url;

        a.download = "TNEA_AI_Report.pdf";

        a.click();

        window.URL.revokeObjectURL(url);

    } finally {

        setDownloading(false);

    }

};
  return (
    <>
      <Navbar onPredictClick={openPredictor} />

      <main>
        {currentPage === "home" && (
  <>
        <HeroSection onGetStarted={openPredictor} />
        <FeaturesSection />
        <HowItWorksSection onNext={openPredictor}/>
          </>
)}
        {showPredictor && (
        <PredictorForm
         onResults={handleResults}
         onLoading={handleLoading}
         isLoading={isLoading}
         communities={communities}
         districts={districts}
         metaLoading={metaLoading}
         metaError={metaError}
         onClose={closePredictor}
         savedFormData={savedFormData}
    setSavedFormData={setSavedFormData}

    
        />
        )}

        {/* Anchor for smooth scroll */}
       {currentPage === "dashboard" && (

<section className="dashboard-page">

  <div className="dashboard-summary">

    <div className="dashboard-top dashboard-header">

        <div className="dashboard-left">

            <h1>
                👋 Hello, {debugInfo?.fullName || "Student"}
            </h1>

            <p>
                Here's your personalized AI prediction report.
            </p>

        </div>
        <div className="dashboard-right">
        <button
            className="download-btn"
            onClick={openPredictor}
        >
            ← New Prediction
        </button>

        <button
    className="download-btn"
    onClick={downloadPDF}
    disabled={downloading}
>
    <i className="fa-solid fa-download"></i>

    {downloading ? "Generating PDF..." : "Download PDF"}
</button>
        </div>
    </div>

</div>
<div className="summary-grid">

<div className="summary-card">

<span><i className="fa-solid fa-trophy"></i></span>
<div className="summary-card-content">
<h4>Rank</h4>

<h2>{debugInfo?.rank}</h2>
</div>

</div>

<div className="summary-card">

<span>👥</span>
<div className="summary-card-content">
<h4>Community</h4>

<h2>{debugInfo?.community}</h2>
</div>
</div>

<div className="summary-card">

<span><i className="fa-solid fa-ranking-star"></i></span>
<div className="summary-card-content">
<h4>Cutoff</h4>

<h2>{debugInfo?.cutoffMark?.toFixed(2)}</h2>
</div>
</div>

<div className="summary-card">

<span><i className="fa-solid fa-graduation-cap"></i></span>
<div className="summary-card-content">
<h4>Preferred Branch</h4>

<h2 style={{fontSize:'13px'}}>
{
    debugInfo?.branches?.length
        ? debugInfo.branches[0]
        : "All Branches"
}
</h2>

{
    debugInfo?.branches?.length > 1 && (
        <span className="branch-more" style={{fontSize:'14px'}}>
            +{debugInfo.branches.length - 1} More
        </span>
    )
}
</div>
</div>

</div>

        <ResultsSection
          recommendations={recommendations}
          error={error}
          hasSearched={hasSearched}
          isLoading={isLoading}
          debugInfo={debugInfo}
          openHostel={openHostel}
          hostelData={hostelData}
          showHostel={showHostel}
          setShowHostel={setShowHostel}
          openWebsite={openWebsite}
          downloadPDF={downloadPDF}
          onRetry={() => {
            setHasSearched(false)
            setError(null)
            setDebugInfo(null)
          }}
        />
        {showHostel && hostelData && (
<div className="popup-overlay">
<div className="hostel-popup">

<div className="popup-header">

<h2>🏨 Hostel & Fees</h2>

<button className="popup-close"
onClick={()=>setShowHostel(false)}
>

✕

</button>

</div>
        <div className="dean-card">
            <i className="fa-solid fa-user-tie"></i>
              <div>
                <span>Dean / Principal : </span>
                  <strong>{hostelData?.dean_principal || "-"}</strong>
              </div>
        </div>
        

<div className="table-wrapper">
<table className="hostel-table">

<thead>

<tr>

<th>Facility</th>

<th>Boys</th>

<th>Girls</th>

</tr>

</thead>

<tbody>

{

Object.entries(hostelData.hostel).map(([key,value])=>(

<tr key={key}>

<td>{key}</td>

<td>{value.boys}</td>

<td>{value.girls}</td>

</tr>

))

}

</tbody>

</table>
</div>
</div>
</div>
)}
        </section>

)}
      </main>

      <footer className="site-footer">

  <div className="footer-container">

    <div className="footer-brand">

      <h2>AI Counseling Predictor</h2>

      <p>
        Helping Students Make Smarter...TNEA Counseling Decisions.
      </p>

    </div>

    <div className="footer-team">
      

      <h3>Development Team</h3>

      <div className="team-grid">

        <div className="member-card">
          <img src="/team/Sudhakar.jpeg" alt="Suthakar" style={{objectPosition:'left 40%'}} />
          
          <h4>
            <a
            href="https://www.linkedin.com/in/suthakar-v-60550a389"
            target="_blank"
            rel="noopener noreferrer"
            className="linkedin-link"
          >
            <i className="fa-brands fa-linkedin"></i>
          </a>Sudhakar V</h4>
        </div>

        <div className="member-card">
          <img src="/team/Thanhgaabarna.jpeg" alt="Member" />
         
          <h4>
             <a
            href="https://www.linkedin.com/in/thangaabarnamayavanathan04?utm_source=share_via&utm_content=profile&utm_medium=member_android"
            target="_blank"
            rel="noopener noreferrer"
            className="linkedin-link"
          >
            <i className="fa-brands fa-linkedin"></i>
          </a>Thanga Abarna</h4>
        </div>

        <div className="member-card">
          <img src="/team/mareeswari.jpeg" alt="Member" />
          
          <h4>
            <a
            href="https://linkedin.com/in/member2"
            target="_blank"
            rel="noopener noreferrer"
            className="linkedin-link"
          >
            <i className="fa-brands fa-linkedin"></i>
          </a>Maresswari</h4>
        </div>

        <div className="member-card">
          <img src="/team/pavithra.jpeg" alt="Member" />
          
          <h4>
            <a
            href="https://www.linkedin.com/in/pavithra013"
            target="_blank"
            rel="noopener noreferrer"
            className="linkedin-link"
          >
            <i className="fa-brands fa-linkedin"></i>
          </a>Pavithra</h4>
        </div>

        <div className="member-card">
          <img src="/team/mathubala.jpeg" alt="Member"  />
          
          <h4><a
            href="https://linkedin.com/in/member2"
            target="_blank"
            rel="noopener noreferrer"
            className="linkedin-link"
          >
            <i className="fa-brands fa-linkedin"></i>
          </a>Mathubala</h4>
        </div>

        <div className="member-card">
          <img src="/team/Vengatesh.jpeg" alt="Member" />
          
          <h4>
            <a
            href="https://linkedin.com/in/member6"
            target="_blank"
            rel="noopener noreferrer"
          >
            <i className="fa-brands fa-linkedin"></i>
          </a>Vengatesh L</h4>
        </div>

          <div className="member-card">
          <img src="/team/Sudhakar.jpeg" alt="Suthakar" style={{objectPosition:'left 40%'}} />
          
          <h4>
            <a
            href="https://www.linkedin.com/in/suthakar-v-60550a389"
            target="_blank"
            rel="noopener noreferrer"
            className="linkedin-link"
          >
            <i className="fa-brands fa-linkedin"></i>
          </a>Sudhakar V</h4>
        </div>

        <div className="member-card">
          <img src="/team/Thanhgaabarna.jpeg" alt="Member" />
         
          <h4>
             <a
            href="https://www.linkedin.com/in/thangaabarnamayavanathan04?utm_source=share_via&utm_content=profile&utm_medium=member_android"
            target="_blank"
            rel="noopener noreferrer"
            className="linkedin-link"
          >
            <i className="fa-brands fa-linkedin"></i>
          </a>Thanga Abarna</h4>
        </div>

        <div className="member-card">
          <img src="/team/mareeswari.jpeg" alt="Member" />
          
          <h4>
            <a
            href="https://linkedin.com/in/member2"
            target="_blank"
            rel="noopener noreferrer"
            className="linkedin-link"
          >
            <i className="fa-brands fa-linkedin"></i>
          </a>Maresswari</h4>
        </div>

        <div className="member-card">
          <img src="/team/pavithra.jpeg" alt="Member" />
          
          <h4>
            <a
            href="https://www.linkedin.com/in/pavithra013"
            target="_blank"
            rel="noopener noreferrer"
            className="linkedin-link"
          >
            <i className="fa-brands fa-linkedin"></i>
          </a>Pavithra</h4>
        </div>

        <div className="member-card">
          <img src="/team/mathubala.jpeg" alt="Member"  />
          
          <h4><a
            href="https://linkedin.com/in/member2"
            target="_blank"
            rel="noopener noreferrer"
            className="linkedin-link"
          >
            <i className="fa-brands fa-linkedin"></i>
          </a>Mathubala</h4>
        </div>

        <div className="member-card">
          <img src="/team/Vengatesh.jpeg" alt="Member" />
          
          <h4>
            <a
            href="https://linkedin.com/in/member6"
            target="_blank"
            rel="noopener noreferrer"
          >
            <i className="fa-brands fa-linkedin"></i>
          </a>Vengatesh L</h4>
        </div>

    

      </div>
      <div className="college-info">

        <h3>Einstein College of Engineering</h3>

        <p>Department of Computer Science and Engineering,Batch 2023 – 2027</p>

        

      </div>
      

    </div>

    

  </div>
  <hr/>

  <div className="footer-bottom">

    © 2027 AI Counseling Predictor Team. All Rights Reserved.
    <p className="footer-source">
    Official Data Source: Anna University / TNEA Counselling Portal ,
    Tamil Nadu.
  </p>
  </div>
  <div className="footer-links">

      

      <a href="#">Contact Us</a>

      <a href="#">Feedback</a>

      <a href="#">Privacy Policy</a>

    </div>

</footer>
    </>
  )
}

export default App
