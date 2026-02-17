import React from 'react'
import { Server, ChevronDown } from 'lucide-react'

function HostSelector({ hosts, selectedHost, onSelect }) {
  // Group hosts by their group
  const groupedHosts = hosts.reduce((acc, host) => {
    const group = host.group || 'other'
    if (!acc[group]) acc[group] = []
    acc[group].push(host)
    return acc
  }, {})

  const groupLabels = {
    nxos: 'Cisco NX-OS',
    ios: 'Cisco IOS',
    vswitch: 'NX-OS Virtual',
    cumulus: 'Cumulus Linux',
    fortigate: 'FortiGate'
  }

  return (
    <div>
      <label htmlFor="host-select" className="block text-sm font-medium text-gray-700 mb-1">
        Select Host
      </label>
      <div className="relative">
        <select
          id="host-select"
          value={selectedHost?.hostname || ''}
          onChange={(e) => {
            const hostname = e.target.value
            const host = hosts.find(h => h.hostname === hostname)
            onSelect(host || null)
          }}
          className="block w-full pl-10 pr-10 py-2 text-base border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 rounded-lg appearance-none bg-white"
        >
          <option value="">-- Select a host --</option>
          {Object.entries(groupedHosts).map(([group, groupHosts]) => (
            <optgroup key={group} label={groupLabels[group] || group}>
              {groupHosts.map(host => (
                <option key={host.hostname} value={host.hostname}>
                  {host.hostname} ({host.ansible_host})
                </option>
              ))}
            </optgroup>
          ))}
        </select>
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Server className="h-5 w-5 text-gray-400" />
        </div>
        <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
          <ChevronDown className="h-5 w-5 text-gray-400" />
        </div>
      </div>

      {selectedHost && (
        <div className="mt-2 text-sm text-gray-500">
          <span className="inline-flex items-center px-2 py-1 rounded-full bg-gray-100 text-gray-700 text-xs">
            {groupLabels[selectedHost.group] || selectedHost.group}
          </span>
          <span className="ml-2">IP: {selectedHost.ansible_host}</span>
        </div>
      )}
    </div>
  )
}

export default HostSelector
