import React, { useState, useEffect } from 'react'
import { Server, Play, Plus, FileText, RefreshCw, AlertCircle, X, ChevronDown, ChevronRight } from 'lucide-react'
import HostSelector from './components/HostSelector'
import AddHostModal from './components/AddHostModal'
import ConfigDashboard from './components/ConfigDashboard'
import DiffViewer from './components/DiffViewer'
import LogsModal from './components/LogsModal'

const API_BASE = '/api'

function App() {
  const [hosts, setHosts] = useState([])
  const [selectedHost, setSelectedHost] = useState(null)
  const [isRunning, setIsRunning] = useState(false)
  const [currentJobId, setCurrentJobId] = useState(null)
  const [jobStatus, setJobStatus] = useState(null)
  const [configData, setConfigData] = useState(null)
  const [changeData, setChangeData] = useState(null)
  const [showAddHost, setShowAddHost] = useState(false)
  const [showLogs, setShowLogs] = useState(false)
  const [error, setError] = useState(null)
  const [summary, setSummary] = useState(null)

  // Fetch hosts on load
  useEffect(() => {
    fetchHosts()
    fetchSummary()
  }, [])

  // Poll for job status when running
  useEffect(() => {
    let interval
    if (currentJobId && isRunning) {
      interval = setInterval(async () => {
        try {
          const response = await fetch(`${API_BASE}/jobs/${currentJobId}`)
          const data = await response.json()
          setJobStatus(data)

          if (data.status === 'completed' || data.status === 'failed') {
            setIsRunning(false)
            if (data.status === 'completed' && selectedHost) {
              // Fetch updated config and changes
              fetchConfig(selectedHost.hostname)
              fetchChanges(selectedHost.hostname)
            }
          }
        } catch (err) {
          console.error('Error polling job status:', err)
        }
      }, 2000)
    }
    return () => clearInterval(interval)
  }, [currentJobId, isRunning, selectedHost])

  const fetchHosts = async () => {
    try {
      const response = await fetch(`${API_BASE}/hosts`)
      const data = await response.json()
      setHosts(data.hosts)
    } catch (err) {
      setError('Failed to fetch hosts')
      console.error(err)
    }
  }

  const fetchSummary = async () => {
    try {
      const response = await fetch(`${API_BASE}/dashboard/summary`)
      const data = await response.json()
      setSummary(data)
    } catch (err) {
      console.error('Failed to fetch summary:', err)
    }
  }

  const fetchConfig = async (hostname) => {
    try {
      const response = await fetch(`${API_BASE}/configs/${hostname}/latest`)
      if (response.ok) {
        const data = await response.json()
        setConfigData(data)
      } else {
        setConfigData(null)
      }
    } catch (err) {
      console.error('Failed to fetch config:', err)
      setConfigData(null)
    }
  }

  const fetchChanges = async (hostname) => {
    try {
      const response = await fetch(`${API_BASE}/changes/${hostname}/latest`)
      if (response.ok) {
        const data = await response.json()
        setChangeData(data)
      } else {
        setChangeData(null)
      }
    } catch (err) {
      console.error('Failed to fetch changes:', err)
      setChangeData(null)
    }
  }

  const handleHostSelect = async (host) => {
    setSelectedHost(host)
    setJobStatus(null)
    setError(null)

    if (host) {
      await fetchConfig(host.hostname)
      await fetchChanges(host.hostname)
    } else {
      setConfigData(null)
      setChangeData(null)
    }
  }

  const handleRun = async () => {
    if (!selectedHost) return

    setIsRunning(true)
    setError(null)
    setJobStatus(null)

    try {
      const response = await fetch(`${API_BASE}/run/${selectedHost.hostname}`, {
        method: 'POST'
      })

      if (!response.ok) {
        throw new Error('Failed to start job')
      }

      const data = await response.json()
      setCurrentJobId(data.job_id)
      setJobStatus({ status: 'running', hostname: selectedHost.hostname })
    } catch (err) {
      setError(err.message)
      setIsRunning(false)
    }
  }

  const handleHostAdded = async () => {
    await fetchHosts()
    setShowAddHost(false)
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Server className="h-8 w-8 text-blue-600" />
              <h1 className="text-2xl font-bold text-gray-900">Network Config Management</h1>
            </div>
            <div className="flex items-center gap-4">
              <button
                onClick={() => setShowLogs(true)}
                className="flex items-center gap-2 px-3 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition"
              >
                <FileText className="h-5 w-5" />
                Logs
              </button>
              <button
                onClick={() => {
                  fetchHosts()
                  fetchSummary()
                }}
                className="flex items-center gap-2 px-3 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition"
              >
                <RefreshCw className="h-5 w-5" />
                Refresh
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
        {/* Summary Cards */}
        {summary && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm text-gray-500">Total Hosts</div>
              <div className="text-2xl font-bold text-gray-900">{summary.total_hosts}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm text-gray-500">Configurations</div>
              <div className="text-2xl font-bold text-gray-900">{summary.total_configs}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm text-gray-500">Changes Detected</div>
              <div className="text-2xl font-bold text-orange-600">{summary.total_changes}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm text-gray-500">Device Groups</div>
              <div className="text-2xl font-bold text-gray-900">{Object.keys(summary.hosts_by_group).length}</div>
            </div>
          </div>
        )}

        {/* Host Selection & Run */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex flex-wrap items-end gap-4">
            <div className="flex-1 min-w-[250px]">
              <HostSelector
                hosts={hosts}
                selectedHost={selectedHost}
                onSelect={handleHostSelect}
              />
            </div>

            <button
              onClick={() => setShowAddHost(true)}
              className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition"
            >
              <Plus className="h-5 w-5" />
              Add Host
            </button>

            <button
              onClick={handleRun}
              disabled={!selectedHost || isRunning}
              className={`flex items-center gap-2 px-6 py-2 rounded-lg font-medium transition ${
                !selectedHost || isRunning
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              {isRunning ? (
                <>
                  <RefreshCw className="h-5 w-5 animate-spin" />
                  Running...
                </>
              ) : (
                <>
                  <Play className="h-5 w-5" />
                  RUN
                </>
              )}
            </button>
          </div>

          {/* Job Status */}
          {jobStatus && (
            <div className={`mt-4 p-3 rounded-lg flex items-center gap-2 ${
              jobStatus.status === 'running' ? 'bg-blue-50 text-blue-700' :
              jobStatus.status === 'completed' ? 'bg-green-50 text-green-700' :
              jobStatus.status === 'failed' ? 'bg-red-50 text-red-700' :
              'bg-gray-50 text-gray-700'
            }`}>
              {jobStatus.status === 'running' && <RefreshCw className="h-4 w-4 animate-spin" />}
              {jobStatus.status === 'completed' && <span className="text-green-600">&#10003;</span>}
              {jobStatus.status === 'failed' && <AlertCircle className="h-4 w-4" />}
              <span className="font-medium">
                {jobStatus.status === 'running' && `Collecting configuration from ${selectedHost?.hostname}...`}
                {jobStatus.status === 'completed' && 'Configuration collection completed!'}
                {jobStatus.status === 'failed' && `Collection failed: ${jobStatus.error || 'Unknown error'}`}
              </span>
              {jobStatus.log_file && (
                <button
                  onClick={() => setShowLogs(true)}
                  className="ml-auto text-sm underline"
                >
                  View Log
                </button>
              )}
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="mt-4 p-3 bg-red-50 text-red-700 rounded-lg flex items-center gap-2">
              <AlertCircle className="h-4 w-4" />
              <span>{error}</span>
              <button onClick={() => setError(null)} className="ml-auto">
                <X className="h-4 w-4" />
              </button>
            </div>
          )}
        </div>

        {/* Dashboard Content */}
        {selectedHost && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Config Dashboard */}
            <div className="bg-white rounded-lg shadow">
              <ConfigDashboard
                hostname={selectedHost.hostname}
                configData={configData}
              />
            </div>

            {/* Changes/Diff Viewer */}
            <div className="bg-white rounded-lg shadow">
              <DiffViewer
                hostname={selectedHost.hostname}
                changeData={changeData}
              />
            </div>
          </div>
        )}

        {/* No host selected */}
        {!selectedHost && (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <Server className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <h2 className="text-xl font-medium text-gray-600 mb-2">Select a Host</h2>
            <p className="text-gray-500">Choose a host from the dropdown above to view its configuration and run collection.</p>
          </div>
        )}

        {/* Recent Changes */}
        {summary && summary.recent_changes.length > 0 && (
          <div className="mt-6 bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Changes</h2>
            <div className="space-y-2">
              {summary.recent_changes.map((change, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-3 bg-orange-50 rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
                    <span className="font-medium text-gray-900">{change.hostname}</span>
                  </div>
                  <span className="text-sm text-gray-500">{change.timestamp.replace('_', ' ')}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      {/* Add Host Modal */}
      {showAddHost && (
        <AddHostModal
          onClose={() => setShowAddHost(false)}
          onHostAdded={handleHostAdded}
        />
      )}

      {/* Logs Modal */}
      {showLogs && (
        <LogsModal
          hostname={selectedHost?.hostname}
          onClose={() => setShowLogs(false)}
        />
      )}
    </div>
  )
}

export default App
