import React, { useState, useEffect } from 'react'
import { X, FileText, AlertCircle, RefreshCw, ChevronDown, ChevronRight, Folder } from 'lucide-react'

const API_BASE = '/api'

function LogsModal({ hostname, onClose }) {
  const [logs, setLogs] = useState([])
  const [selectedLog, setSelectedLog] = useState(null)
  const [logContent, setLogContent] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (hostname) {
      fetchLogs()
    }
  }, [hostname])

  const fetchLogs = async () => {
    if (!hostname) return

    setLoading(true)
    setError(null)

    try {
      const response = await fetch(`${API_BASE}/logs/${hostname}`)
      if (!response.ok) {
        throw new Error('Failed to fetch logs')
      }
      const data = await response.json()
      setLogs(data.logs)

      // Auto-select latest log
      if (data.logs.length > 0) {
        await loadLogContent(data.logs[0])
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const loadLogContent = async (log) => {
    setSelectedLog(log)
    setLoading(true)

    try {
      const response = await fetch(`${API_BASE}/logs/${hostname}/latest`)
      if (!response.ok) {
        throw new Error('Failed to load log content')
      }
      const data = await response.json()
      setLogContent(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const formatSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl mx-4 max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b flex-shrink-0">
          <div className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-blue-600" />
            <h2 className="text-lg font-semibold text-gray-900">
              Logs {hostname && `- ${hostname}`}
            </h2>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={fetchLogs}
              disabled={loading || !hostname}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded"
              title="Refresh"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-hidden flex">
          {/* Log List */}
          <div className="w-64 border-r flex-shrink-0 overflow-y-auto">
            <div className="p-3 bg-gray-50 border-b">
              <h3 className="text-sm font-medium text-gray-700">Log Files</h3>
            </div>
            {!hostname ? (
              <div className="p-4 text-sm text-gray-500">
                Select a host to view logs
              </div>
            ) : logs.length === 0 ? (
              <div className="p-4 text-sm text-gray-500">
                No logs available
              </div>
            ) : (
              <div className="divide-y">
                {logs.map((log, idx) => (
                  <button
                    key={idx}
                    onClick={() => loadLogContent(log)}
                    className={`w-full text-left p-3 hover:bg-gray-50 transition ${
                      selectedLog?.filename === log.filename ? 'bg-blue-50' : ''
                    }`}
                  >
                    <div className="text-sm font-medium text-gray-900 truncate">
                      {log.filename}
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      {log.timestamp} &bull; {formatSize(log.size)}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Log Content */}
          <div className="flex-1 flex flex-col overflow-hidden">
            {logContent ? (
              <>
                {/* Log Info */}
                <div className="p-4 border-b flex-shrink-0">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium text-gray-900">{logContent.filename}</h3>
                      <div className="flex items-center gap-2 mt-1 text-sm text-gray-500">
                        <Folder className="h-4 w-4" />
                        <span className="truncate max-w-md" title={logContent.path}>
                          {logContent.path}
                        </span>
                      </div>
                    </div>
                    {logContent.has_errors && (
                      <div className="flex items-center gap-1 px-2 py-1 bg-red-100 text-red-700 rounded text-sm">
                        <AlertCircle className="h-4 w-4" />
                        {logContent.errors.length} error(s)
                      </div>
                    )}
                  </div>
                </div>

                {/* Errors Section */}
                {logContent.has_errors && (
                  <div className="border-b p-4 bg-red-50 flex-shrink-0">
                    <h4 className="font-medium text-red-700 mb-2 flex items-center gap-2">
                      <AlertCircle className="h-4 w-4" />
                      Errors Detected
                    </h4>
                    <div className="space-y-1 max-h-32 overflow-y-auto">
                      {logContent.errors.map((err, idx) => (
                        <div
                          key={idx}
                          className="text-sm text-red-600 font-mono bg-red-100 px-2 py-1 rounded"
                        >
                          {err}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Log Content */}
                <div className="flex-1 overflow-auto p-4 bg-gray-900">
                  <pre className="font-mono text-xs text-gray-100 whitespace-pre-wrap">
                    {logContent.content.split('\n').map((line, idx) => {
                      let className = ''
                      if (/error|failed|fatal/i.test(line)) {
                        className = 'text-red-400'
                      } else if (/warn/i.test(line)) {
                        className = 'text-yellow-400'
                      } else if (/ok|success|changed/i.test(line)) {
                        className = 'text-green-400'
                      }
                      return (
                        <div key={idx} className={className}>
                          <span className="text-gray-500 select-none mr-3">
                            {String(idx + 1).padStart(4, ' ')}
                          </span>
                          {line}
                        </div>
                      )
                    })}
                  </pre>
                </div>
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center text-gray-500">
                {loading ? (
                  <div className="flex items-center gap-2">
                    <RefreshCw className="h-5 w-5 animate-spin" />
                    Loading...
                  </div>
                ) : error ? (
                  <div className="flex items-center gap-2 text-red-600">
                    <AlertCircle className="h-5 w-5" />
                    {error}
                  </div>
                ) : (
                  <div className="text-center">
                    <FileText className="h-12 w-12 mx-auto mb-3 text-gray-300" />
                    <p>Select a log file to view</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default LogsModal
