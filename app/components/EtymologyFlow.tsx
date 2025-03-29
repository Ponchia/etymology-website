'use client';

import React, { useMemo } from 'react';
import ReactFlow, {
  Node,
  Edge,
  useNodesState,
  useEdgesState,
  MarkerType,
  Handle,
  Position
} from 'reactflow';
import 'reactflow/dist/style.css';
import { RootWord, languageColors } from '../types';
import { motion } from 'framer-motion';

// Custom node component
function EtymologyNode({ data, id }: { data: RootWord; id: string }) {
  const languageColor = data.language && languageColors[data.language] 
    ? languageColors[data.language].split(' ')[0] 
    : 'bg-gray-700';

  // Only show source handle on the main node
  const showSourceHandle = id === 'main';
  
  // Show target handle on all nodes except the main one
  const showTargetHandle = id !== 'main';

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="bg-white p-4 rounded-lg border-2 border-gray-300 shadow-md max-w-[250px]"
    >
      {showSourceHandle && (
        <Handle
          type="source"
          position={Position.Bottom}
          id="bottom"
          style={{ background: '#555', width: '8px', height: '8px' }}
        />
      )}
      
      {showTargetHandle && (
        <Handle
          type="target"
          position={Position.Top}
          id="top"
          style={{ background: '#555', width: '8px', height: '8px' }}
        />
      )}
      
      <h3 className="text-lg font-bold text-gray-800 mb-1">{data.word}</h3>
      <span className={`inline-block rounded-full px-2 py-0.5 text-xs text-white ${languageColor} mb-2`}>
        {data.language}
      </span>
      {data.definition && (
        <p className="text-sm text-gray-600 mb-2">{data.definition}</p>
      )}
      {data.year && (
        <div className="text-xs text-gray-500">
          {data.year > 0 ? data.year : data.year < 0 ? `${Math.abs(data.year)} BCE` : 'unknown'}
        </div>
      )}
    </motion.div>
  );
}

const nodeTypes = {
  etymologyNode: EtymologyNode
};

export default function EtymologyFlow({ words }: { words: RootWord[] }) {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  
  // Create the node structure
  useMemo(() => {
    if (!words || words.length === 0) return;
    
    const newNodes: Node[] = [];
    
    // Map to track created nodes
    const nodeMap = new Map<string, string>();
    
    // Main word at the top center
    const mainWord = words[0];
    newNodes.push({
      id: 'main',
      type: 'etymologyNode',
      position: { x: 0, y: 0 },
      data: mainWord
    });
    nodeMap.set(mainWord.word, 'main');
    
    // Position remaining words in rows below
    const VERTICAL_SPACE = 200;
    const HORIZONTAL_SPACE = 250;
    
    // Group words by language
    const languageGroups: Record<string, RootWord[]> = {};
    for (let i = 1; i < words.length; i++) {
      const word = words[i];
      if (!languageGroups[word.language]) {
        languageGroups[word.language] = [];
      }
      languageGroups[word.language].push(word);
    }
    
    // Create nodes by language groups
    let rowIndex = 1;
    for (const language in languageGroups) {
      const wordsInGroup = languageGroups[language];
      
      // Calculate total width needed for this row
      const totalWidth = (wordsInGroup.length - 1) * HORIZONTAL_SPACE;
      const startX = -totalWidth / 2;
      
      // Create nodes for this language
      wordsInGroup.forEach((word, index) => {
        const nodeId = `${language}_${index}`;
        const x = startX + index * HORIZONTAL_SPACE;
        const y = rowIndex * VERTICAL_SPACE;
        
        newNodes.push({
          id: nodeId,
          type: 'etymologyNode',
          position: { x, y },
          data: word
        });
        
        nodeMap.set(word.word, nodeId);
      });
      
      rowIndex++;
    }
    
    setNodes(newNodes);
  }, [words, setNodes]);
  
  // Create edges separately after nodes
  useMemo(() => {
    if (!nodes || nodes.length <= 1) return;
    
    const newEdges: Edge[] = [];
    
    // Create edges from main node to all other nodes
    nodes.forEach(node => {
      if (node.id !== 'main') {
        newEdges.push({
          id: `e_main_to_${node.id}`,
          source: 'main',
          target: node.id,
          sourceHandle: 'bottom',
          targetHandle: 'top',
          type: 'default',
          animated: false,
          markerEnd: {
            type: MarkerType.Arrow,
            color: '#333',
            width: 15,
            height: 15
          },
          style: { 
            stroke: '#333', 
            strokeWidth: 2,
            opacity: 1
          }
        });
      }
    });
    
    setEdges(newEdges);
  }, [nodes, setEdges]);
  
  if (!words || words.length === 0) {
    return <div className="flex h-full items-center justify-center">No etymology data available</div>;
  }
  
  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      nodeTypes={nodeTypes}
      elevateEdgesOnSelect={true}
      elevateNodesOnSelect={false}
      fitView
      fitViewOptions={{ padding: 0.3 }}
      defaultEdgeOptions={{
        type: 'default',
        animated: false,
        style: { 
          stroke: '#333', 
          strokeWidth: 2,
          opacity: 0.8
        }
      }}
      style={{ 
        background: 'rgb(245, 245, 245)',
        width: '100%',
        height: '100%'
      }}
      proOptions={{ hideAttribution: false }}
      className="h-full w-full"
    />
  );
} 