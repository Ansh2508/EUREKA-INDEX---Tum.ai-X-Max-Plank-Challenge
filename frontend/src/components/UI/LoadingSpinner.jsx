import './LoadingSpinner.css'

function LoadingSpinner({ size = 'medium', message = 'Loading...', progress = null }) {
  return (
    <div className="loading-container">
      <div className="spinner-wrapper">
        <div className={`loading-spinner ${size}`}></div>
        {progress !== null && (
          <div className="progress-circle">
            <svg className="progress-ring" width="80" height="80">
              <circle
                className="progress-ring-circle"
                stroke="#e5e7eb"
                strokeWidth="4"
                fill="transparent"
                r="36"
                cx="40"
                cy="40"
              />
              <circle
                className="progress-ring-progress"
                stroke="#3b82f6"
                strokeWidth="4"
                fill="transparent"
                r="36"
                cx="40"
                cy="40"
                style={{
                  strokeDasharray: `${2 * Math.PI * 36}`,
                  strokeDashoffset: `${2 * Math.PI * 36 * (1 - progress / 100)}`,
                }}
              />
            </svg>
            <div className="progress-percentage">
              {Math.round(progress)}%
            </div>
          </div>
        )}
      </div>
      {message && <p className="loading-message">{message}</p>}
    </div>
  )
}

export default LoadingSpinner