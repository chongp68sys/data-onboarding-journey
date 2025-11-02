import React, { useCallback, useState, useEffect, useRef, DragEvent } from 'react';
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  BackgroundVariant,
  useReactFlow,
  type Edge,
  type OnConnect,
  type Node,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

// Empty canvas - no initial nodes or edges
const initialNodes: Node[] = [];

const initialEdges: Edge[] = [];

let id = 0;
const getId = () => `dndnode_${id++}`;

export default function FlowCanvas() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  const containerRef = useRef<HTMLDivElement>(null);
  const { screenToFlowPosition } = useReactFlow();

  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        const { clientWidth, clientHeight } = containerRef.current;
        if (clientWidth > 0 && clientHeight > 0) {
          setDimensions({ width: clientWidth, height: clientHeight });
        }
      }
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);

    return () => {
      window.removeEventListener('resize', updateDimensions);
    };
  }, []);

  const onConnect: OnConnect = useCallback(
    (params) => setEdges((eds) => addEdge(params, eds)),
    [setEdges],
  );

  const onDragOver = useCallback((event: DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event: DragEvent) => {
      event.preventDefault();

      const type = event.dataTransfer.getData('application/reactflow');
      const label = event.dataTransfer.getData('application/nodelabel');

      // Check if the dropped element is valid
      if (typeof type === 'undefined' || !type) {
        return;
      }

      const position = screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });

      const getNodeStyle = (nodeType: string) => {
        if (nodeType.includes('Agent') || nodeType.includes('agent')) {
          return {
            background: 'linear-gradient(135deg, #7c3aed 0%, #8b5cf6 100%)',
            color: 'white',
            border: '2px solid #8b5cf6',
            borderRadius: '12px',
            padding: '12px 20px',
            fontSize: '14px',
            fontWeight: '600',
            minWidth: '160px',
            textAlign: 'center' as const,
            boxShadow: '0 4px 20px rgba(124, 58, 237, 0.25)',
          };
        } else if (nodeType.includes('Upload') || nodeType.includes('Source') || nodeType.includes('sftp') || nodeType.includes('file')) {
          return {
            background: 'linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%)',
            color: 'white',
            border: '2px solid #0284c7',
            borderRadius: '12px',
            padding: '12px 20px',
            fontSize: '14px',
            fontWeight: '600',
            minWidth: '140px',
            textAlign: 'center' as const,
            boxShadow: '0 4px 20px rgba(14, 165, 233, 0.25)',
          };
        } else {
          return {
            background: 'linear-gradient(135deg, #6b7280 0%, #4b5563 100%)',
            color: 'white',
            border: '2px solid #6b7280',
            borderRadius: '12px',
            padding: '12px 20px',
            fontSize: '14px',
            fontWeight: '600',
            minWidth: '120px',
            textAlign: 'center' as const,
            boxShadow: '0 4px 20px rgba(107, 114, 128, 0.25)',
          };
        }
      };

      const newNode: Node = {
        id: getId(),
        type: 'default',
        position,
        data: { 
          label,
          nodeType: type,
        },
        style: getNodeStyle(type),
      };

      setNodes((nds) => nds.concat(newNode));
    },
    [screenToFlowPosition, setNodes],
  );

  return (
    <div 
      ref={containerRef}
      className="h-full w-full bg-slate-900" 
      style={{ width: '100%', height: '100%', minHeight: '400px' }}
    >
      <div style={{ width: `${dimensions.width}px`, height: `${dimensions.height}px` }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onDrop={onDrop}
          onDragOver={onDragOver}
          className="bg-slate-900"
          proOptions={{ hideAttribution: true }}
          fitView
        >
        <Controls 
          className="!bg-slate-800 !border-slate-600"
          style={{
            backgroundColor: '#1e293b',
            borderColor: '#475569',
            borderRadius: '8px',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)',
          }}
        />
        <MiniMap 
          className="!bg-slate-800 !border-slate-600"
          style={{
            backgroundColor: '#1e293b',
            borderColor: '#475569',
            borderRadius: '8px',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)',
          }}
          maskColor="rgba(15, 23, 42, 0.7)"
          nodeColor={(node) => {
            const style = node.style;
            if (style?.background?.includes('7c3aed')) return '#7c3aed'; // Intrum Purple
            if (style?.background?.includes('0ea5e9')) return '#0ea5e9'; // Blue
            return '#6b7280'; // Gray
          }}
        />
        <Background 
          variant={BackgroundVariant.Dots} 
          gap={25} 
          size={1.5} 
          color="#475569"
        />
        </ReactFlow>
      </div>
    </div>
  );
}