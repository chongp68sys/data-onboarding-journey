import React from 'react';

interface NodeType {
  id: string;
  type: string;
  label: string;
  category: 'agents' | 'data' | 'blocks';
  icon: string;
  color: string;
}

// Simple node types based on backend agents
const nodeTypes: NodeType[] = [
  // AI Agents (Purple - Intrum brand color)
  {
    id: 'file-ingestion-agent',
    type: 'fileIngestionAgent',
    label: 'File Ingestion',
    category: 'agents',
    icon: '🤖',
    color: 'bg-purple-600',
  },
  {
    id: 'data-mapping-agent',
    type: 'dataMappingAgent',
    label: 'Data Mapping',
    category: 'agents',
    icon: '🧠',
    color: 'bg-purple-600',
  },
  {
    id: 'data-quality-agent',
    type: 'dataQualityAgent',
    label: 'Data Quality',
    category: 'agents',
    icon: '🔍',
    color: 'bg-purple-600',
  },
  
  // Data Sources (Blue)
  {
    id: 'file-upload',
    type: 'fileUpload',
    label: 'File Upload',
    category: 'data',
    icon: '📁',
    color: 'bg-blue-500',
  },
  {
    id: 'sftp-source',
    type: 'sftpSource',
    label: 'SFTP Source',
    category: 'data',
    icon: '🔗',
    color: 'bg-blue-500',
  },
  
  // Processing Blocks (Gray)
  {
    id: 'filter-block',
    type: 'filterBlock',
    label: 'Filter',
    category: 'blocks',
    icon: '⚗️',
    color: 'bg-gray-600',
  },
  {
    id: 'export-data',
    type: 'exportData',
    label: 'Export',
    category: 'blocks',
    icon: '💾',
    color: 'bg-gray-600',
  },
];

const categoryLabels = {
  agents: 'AI Agents',
  data: 'Data Sources',
  blocks: 'Processing'
};

export default function NodePalette() {
  const categories = Object.keys(categoryLabels) as (keyof typeof categoryLabels)[];

  return (
    <div className="w-64 h-full bg-slate-800 border-r border-slate-700 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-slate-700">
        <h2 className="text-lg font-semibold text-white">Components</h2>
      </div>

      {/* Node Categories */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {categories.map((category) => {
          const nodes = nodeTypes.filter(node => node.category === category);
          return (
            <div key={category} className="space-y-3">
              <h3 className="text-sm font-medium text-gray-300 uppercase tracking-wide">
                {categoryLabels[category]}
              </h3>
              <div className="space-y-2">
                {nodes.map((node) => (
                  <div
                    key={node.id}
                    className="flex items-center p-3 bg-slate-900/50 rounded-lg border border-slate-700 cursor-move hover:bg-slate-900 hover:border-slate-600 hover:scale-[1.02] transition-all duration-200 active:scale-95"
                    draggable
                    onDragStart={(e) => {
                      e.dataTransfer.setData('application/reactflow', node.type);
                      e.dataTransfer.setData('application/nodelabel', node.label);
                      e.dataTransfer.effectAllowed = 'move';
                      // Add visual feedback during drag
                      e.currentTarget.style.opacity = '0.5';
                    }}
                    onDragEnd={(e) => {
                      // Reset visual feedback after drag
                      e.currentTarget.style.opacity = '1';
                    }}
                  >
                    <div className={`w-8 h-8 rounded-lg ${node.color} flex items-center justify-center mr-3 text-sm`}>
                      {node.icon}
                    </div>
                    <span className="text-sm text-white font-medium">
                      {node.label}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}