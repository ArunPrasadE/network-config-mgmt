import React, { useState } from 'react'
import { ChevronDown, ChevronRight, FileText, Clock, Copy, Check } from 'lucide-react'

function ConfigDashboard({ hostname, configData }) {
  const [expandedSections, setExpandedSections] = useState({})
  const [copiedSection, setCopiedSection] = useState(null)

  if (!configData) {
    return (
      <div className="p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <FileText className="h-5 w-5 text-blue-600" />
          Configuration
        </h2>
        <div className="text-center py-8 text-gray-500">
          <FileText className="h-12 w-12 mx-auto mb-3 text-gray-300" />
          <p>No configuration data available.</p>
          <p className="text-sm mt-1">Run collection to fetch configuration.</p>
        </div>
      </div>
    )
  }

  const toggleSection = (title) => {
    setExpandedSections(prev => ({
      ...prev,
      [title]: !prev[title]
    }))
  }

  const copyToClipboard = async (content, title) => {
    try {
      await navigator.clipboard.writeText(content)
      setCopiedSection(title)
      setTimeout(() => setCopiedSection(null), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  const formatTimestamp = (ts) => {
    if (!ts) return ''
    return ts.replace('_', ' ')
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
          <FileText className="h-5 w-5 text-blue-600" />
          Configuration
        </h2>
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <Clock className="h-4 w-4" />
          {formatTimestamp(configData.timestamp)}
        </div>
      </div>

      <div className="text-sm text-gray-500 mb-4">
        {configData.filename}
      </div>

      {/* Config Sections */}
      <div className="space-y-3 max-h-[600px] overflow-y-auto pr-2">
        {configData.sections && configData.sections.map((section, idx) => (
          <div key={idx} className="border rounded-lg overflow-hidden">
            <button
              onClick={() => toggleSection(section.title)}
              className="w-full flex items-center justify-between px-4 py-3 bg-gray-50 hover:bg-gray-100 transition"
            >
              <div className="flex items-center gap-2">
                {expandedSections[section.title] ? (
                  <ChevronDown className="h-4 w-4 text-gray-500" />
                ) : (
                  <ChevronRight className="h-4 w-4 text-gray-500" />
                )}
                <span className="font-medium text-gray-700">{section.title}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-400">
                  {section.content.split('\n').length} lines
                </span>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    copyToClipboard(section.content, section.title)
                  }}
                  className="p-1 hover:bg-gray-200 rounded"
                  title="Copy section"
                >
                  {copiedSection === section.title ? (
                    <Check className="h-4 w-4 text-green-600" />
                  ) : (
                    <Copy className="h-4 w-4 text-gray-400" />
                  )}
                </button>
              </div>
            </button>

            {expandedSections[section.title] && (
              <div className="p-4 bg-gray-900 text-gray-100 font-mono text-xs overflow-x-auto max-h-96 overflow-y-auto">
                <pre className="whitespace-pre-wrap">{section.content}</pre>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Show raw config if no sections parsed */}
      {(!configData.sections || configData.sections.length === 0) && configData.content && (
        <div className="border rounded-lg overflow-hidden">
          <div className="px-4 py-3 bg-gray-50 font-medium text-gray-700">
            Raw Configuration
          </div>
          <div className="p-4 bg-gray-900 text-gray-100 font-mono text-xs overflow-x-auto max-h-[500px] overflow-y-auto">
            <pre className="whitespace-pre-wrap">{configData.content}</pre>
          </div>
        </div>
      )}
    </div>
  )
}

export default ConfigDashboard
