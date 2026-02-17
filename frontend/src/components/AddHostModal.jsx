import React, { useState, useEffect } from 'react'
import { X, Plus, AlertCircle } from 'lucide-react'

const API_BASE = '/api'

function AddHostModal({ onClose, onHostAdded }) {
  const [groups, setGroups] = useState([])
  const [formData, setFormData] = useState({
    hostname: '',
    group: '',
    ansible_host: '',
    ansible_connection: '',
    ansible_network_os: ''
  })
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchGroups()
  }, [])

  const fetchGroups = async () => {
    try {
      const response = await fetch(`${API_BASE}/groups`)
      const data = await response.json()
      setGroups(data.groups)
      if (data.groups.length > 0) {
        setFormData(prev => ({ ...prev, group: data.groups[0].name }))
      }
    } catch (err) {
      console.error('Failed to fetch groups:', err)
    }
  }

  // Connection options based on device type
  const connectionOptions = {
    nxos: {
      connection: 'ansible.netcommon.network_cli',
      network_os: 'cisco.nxos.nxos'
    },
    ios: {
      connection: 'ansible.netcommon.network_cli',
      network_os: 'cisco.ios.ios'
    },
    vswitch: {
      connection: 'ansible.netcommon.network_cli',
      network_os: 'cisco.nxos.nxos'
    },
    cumulus: {
      connection: 'ssh',
      network_os: ''
    },
    fortigate: {
      connection: 'local',
      network_os: ''
    }
  }

  const handleGroupChange = (group) => {
    const options = connectionOptions[group] || { connection: '', network_os: '' }
    setFormData(prev => ({
      ...prev,
      group,
      ansible_connection: options.connection,
      ansible_network_os: options.network_os
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    // Validate
    if (!formData.hostname || !formData.group || !formData.ansible_host) {
      setError('Hostname, group, and IP/hostname are required')
      setLoading(false)
      return
    }

    // Validate hostname format
    if (!/^[a-zA-Z0-9-_]+$/.test(formData.hostname)) {
      setError('Hostname can only contain letters, numbers, hyphens, and underscores')
      setLoading(false)
      return
    }

    try {
      const response = await fetch(`${API_BASE}/hosts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      })

      if (!response.ok) {
        const errData = await response.json()
        throw new Error(errData.detail || 'Failed to add host')
      }

      onHostAdded()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
        <div className="flex items-center justify-between px-6 py-4 border-b">
          <h2 className="text-lg font-semibold text-gray-900">Add New Host</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="p-3 bg-red-50 text-red-700 rounded-lg flex items-center gap-2 text-sm">
              <AlertCircle className="h-4 w-4 flex-shrink-0" />
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Hostname *
            </label>
            <input
              type="text"
              value={formData.hostname}
              onChange={(e) => setFormData(prev => ({ ...prev, hostname: e.target.value }))}
              placeholder="e.g., switch-core-01"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Device Group *
            </label>
            <select
              value={formData.group}
              onChange={(e) => handleGroupChange(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {groups.map(group => (
                <option key={group.name} value={group.name}>
                  {group.description}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              IP Address / Hostname *
            </label>
            <input
              type="text"
              value={formData.ansible_host}
              onChange={(e) => setFormData(prev => ({ ...prev, ansible_host: e.target.value }))}
              placeholder="e.g., 192.168.1.1 or device.example.com"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Connection Type
            </label>
            <input
              type="text"
              value={formData.ansible_connection}
              onChange={(e) => setFormData(prev => ({ ...prev, ansible_connection: e.target.value }))}
              placeholder="Auto-filled based on group"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-gray-50"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Network OS
            </label>
            <input
              type="text"
              value={formData.ansible_network_os}
              onChange={(e) => setFormData(prev => ({ ...prev, ansible_network_os: e.target.value }))}
              placeholder="Auto-filled based on group"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-gray-50"
            />
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
            >
              <Plus className="h-4 w-4" />
              {loading ? 'Adding...' : 'Add Host'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default AddHostModal
