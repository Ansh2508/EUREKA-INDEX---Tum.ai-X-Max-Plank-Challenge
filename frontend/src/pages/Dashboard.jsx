import { useState } from 'react'
import './Dashboard.css'

function Dashboard() {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)

  const handleFileChange = (e) => {
    setFile(e.target.files[0])
    setError(null)
  }

  const handleAnalyze = async () => {
    if (!file) {
      setError('Please select a JSON file')
      return
    }

    setLoading(true)
    setError(null)
    setResults(null)

    try {
      const reader = new FileReader()
      reader.onload = async (e) => {
        try {
          const payload = JSON.parse(e.target.result)
          
          const response = await fetch('http://localhost:8000/results/intelligence_analysis', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
          })

          if (!response.ok) {
            throw new Error('Analysis failed')
          }

          const data = await response.json()
          setResults(data)
        } catch (err) {
          setError(err.message)
        } finally {
          setLoading(false)
        }
      }
      reader.readAsText(file)
    } catch (err) {
      setError(err.message)
      setLoading(false)
    }
  }

  return (
    <div className="dashboard-page">
      <div className="dashboard-container">
        <h1>Patent Intelligence Dashboard</h1>
        <p className="subtitle">
          Upload publication and patent data for comprehensive intelligence analysis
        </p>

        <div className="upload-section">
          <div className="file-input-wrapper">
            <input
              type="file"
              id="dataFile"
              accept=".json"
              onChange={handleFileChange}
              className="file-input"
            />
            <label htmlFor="dataFile" className="file-label">
              {file ? file.name : 'Choose JSON file'}
            </label>
          </div>
          <button
            onClick={handleAnalyze}
            className="btn btn-primary"
            disabled={loading || !file}
          >
            {loading ? 'Analyzing...' : 'Analyze Data'}
          </button>
        </div>

        {error && (
          <div className="error-message">
            <strong>Error:</strong> {error}
          </div>
        )}

        {results && (
          <div className="dashboard-results">
            <section className="result-section">
              <h2>Key Players</h2>
              <div className="tables-grid">
                <div className="table-container">
                  <h3>Top Authors</h3>
                  <table>
                    <thead>
                      <tr>
                        <th>Author</th>
                        <th>Publications</th>
                      </tr>
                    </thead>
                    <tbody>
                      {results.top_authors?.map((author, index) => (
                        <tr key={index}>
                          <td>{author[0]}</td>
                          <td>{author[1]}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                <div className="table-container">
                  <h3>Top Institutions</h3>
                  <table>
                    <thead>
                      <tr>
                        <th>Institution</th>
                        <th>Publications</th>
                      </tr>
                    </thead>
                    <tbody>
                      {results.top_institutions?.map((inst, index) => (
                        <tr key={index}>
                          <td>{inst[0]}</td>
                          <td>{inst[1]}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </section>

            <section className="result-section">
              <h2>Emerging Trends</h2>
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>Topic</th>
                      <th>Count</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(results.topic_counts || {}).map(([topic, count], index) => (
                      <tr key={index}>
                        <td>{topic}</td>
                        <td>{count}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="underexplored">
                <h3>Underexplored Topics</h3>
                <p>{results.underexplored_topics?.join(', ')}</p>
              </div>
            </section>

            <section className="result-section">
              <h2>Research-Patent Matches</h2>
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>Publication</th>
                      <th>Patent</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.research_patent_matches?.map((match, index) => (
                      <tr key={index}>
                        <td>{match[0]}</td>
                        <td>{match[1]}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>

            <section className="result-section">
              <h2>Priority Opportunities</h2>
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>Publication</th>
                      <th>Topic</th>
                      <th>Citations</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.priority_opportunities?.map((opp, index) => (
                      <tr key={index}>
                        <td>{opp[0]}</td>
                        <td>{opp[1]}</td>
                        <td>{opp[2]}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          </div>
        )}
      </div>
    </div>
  )
}

export default Dashboard

