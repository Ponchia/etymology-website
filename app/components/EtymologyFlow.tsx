'use client';

import React, { useMemo } from 'react';
import ReactFlow, {
  Node,
  Edge,
  useNodesState,
  useEdgesState,
  MarkerType
} from 'reactflow';
import 'reactflow/dist/style.css';
import { RootWord, languageColors } from '../types';
import { motion } from 'framer-motion';

// Custom node component
function EtymologyNode({ data }: { data: RootWord }) {
  const languageColor = data.language && languageColors[data.language] 
    ? languageColors[data.language].split(' ')[0] 
    : 'bg-gray-700';

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm max-w-[250px]"
    >
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
    const newEdges: Edge[] = [];
    
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
        
        // Connect to the main word
        newEdges.push({
          id: `e_main_to_${nodeId}`,
          source: 'main',
          target: nodeId,
          type: 'smoothstep',
          markerEnd: {
            type: MarkerType.ArrowClosed,
            color: '#888',
            width: 12,
            height: 12
          },
          style: { stroke: '#888', strokeWidth: 1 }
        });
      });
      
      rowIndex++;
    }
    
    setNodes(newNodes);
    setEdges(newEdges);
  }, [words, setNodes, setEdges]);
  
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
      fitView
      fitViewOptions={{ padding: 0.3 }}
      className="h-full w-full"
    />
  );
} 