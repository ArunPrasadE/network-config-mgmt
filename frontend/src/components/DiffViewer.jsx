import React, { useState } from 'react'
import { GitCompare, Clock, Plus, Minus, ChevronDown, ChevronRight } from 'lucide-react'

function DiffViewer({ hostname, changeData }) {
  const [showRaw, setShowRaw] = useState(false)

  if (!changeData || !changeData.has_changes) {
    return (
      <div className="p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <GitCompare className="h-5 w-5 text-orange-600" />
          Configuration Changes
        </h2>
        <div className="text-center py-8 text-gray-500">
          <GitCompare className="h-12 w-12 mx-auto mb-3 text-gray-300" />
          <p>No changes detected.</p>
          <p className="text-sm mt-1">Configuration matches the previous baseline.</p>
        </div>
      </div>
    )
  }

  const formatTimestamp = (ts) => {
    if (!ts) return ''
    return ts.replace('_', ' ')
  }

  const { diff } = changeData

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
          <GitCompare className="h-5 w-5 text-orange-600" />
          Configuration Changes
        </h2>
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <Clock className="h-4 w-4" />
          {formatTimestamp(changeData.timestamp)}
        </div>
      </div>

      {/* Change Summary */}
      <div className="flex gap-4 mb-4">
        <div className="flex items-center gap-2 px-3 py-2 bg-green-50 rounded-lg">
          <Plus className="h-4 w-4 text-green-600" />
          <span className="text-green-700 font-medium">{diff.additions_count} additions</span>
        </div>
        <div className="flex items-center gap-2 px-3 py-2 bg-red-50 rounded-lg">
          <Minus className="h-4 w-4 text-red-600" />
          <span className="text-red-700 font-medium">{diff.removals_count} removals</span>
        </div>
      </div>

      {/* Toggle View */}
      <div className="mb-4">
        <button
          onClick={() => setShowRaw(!showRaw)}
          className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900"
        >
          {showRaw ? (
            <ChevronDown className="h-4 w-4" />
          ) : (
            <ChevronRight className="h-4 w-4" />
          )}
          {showRaw ? 'Hide raw diff' : 'Show raw diff'}
        </button>
      </div>

      {/* Visual Diff */}
      <div className="space-y-4 max-h-[500px] overflow-y-auto">
        {/* Removals */}
        {diff.removals.length > 0 && (
          <div className="border border-red-200 rounded-lg overflow-hidden">
            <div className="px-4 py-2 bg-red-50 font-medium text-red-700 flex items-center gap-2">
              <Minus className="h-4 w-4" />
              Removed Lines ({diff.removals.length})
            </div>
            <div className="p-3 bg-red-50/30 font-mono text-xs overflow-x-auto max-h-48 overflow-y-auto">
              {diff.removals.map((line, idx) => (
                <div key={idx} className="px-2 py-1 bg-red-100 border-l-2 border-red-500 mb-1 text-red-800">
                  {line || <span className="text-gray-400 italic">(empty line)</span>}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Additions */}
        {diff.additions.length > 0 && (
          <div className="border border-green-200 rounded-lg overflow-hidden">
            <div className="px-4 py-2 bg-green-50 font-medium text-green-700 flex items-center gap-2">
              <Plus className="h-4 w-4" />
              Added Lines ({diff.additions.length})
            </div>
            <div className="p-3 bg-green-50/30 font-mono text-xs overflow-x-auto max-h-48 overflow-y-auto">
              {diff.additions.map((line, idx) => (
                <div key={idx} className="px-2 py-1 bg-green-100 border-l-2 border-green-500 mb-1 text-green-800">
                  {line || <span className="text-gray-400 italic">(empty line)</span>}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Raw Diff */}
      {showRaw && changeData.content && (
        <div className="mt-4 border rounded-lg overflow-hidden">
          <div className="px-4 py-2 bg-gray-100 font-medium text-gray-700">
            Raw Diff Output
          </div>
          <div className="p-4 bg-gray-900 font-mono text-xs overflow-x-auto max-h-[400px] overflow-y-auto">
            <pre className="whitespace-pre-wrap">
              {changeData.content.split('\n').map((line, idx) => {
                let className = 'text-gray-300'
                if (line.startsWith('+') && !line.startsWith('+++')) {
                  className = 'text-green-400 bg-green-900/30'
                } else if (line.startsWith('-') && !line.startsWith('---')) {
                  className = 'text-red-400 bg-red-900/30'
                } else if (line.startsWith('@@')) {
                  className = 'text-blue-400'
                }
                return (
                  <div key={idx} className={className}>
                    {line}
                  </div>
                )
              })}
            </pre>
          </div>
        </div>
      )}

      <div className="mt-4 text-sm text-gray-500">
        File: {changeData.filename}
      </div>
    </div>
  )
}

export default DiffViewer
