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
import { RootWord, languageColors, EtymologyWord } from '../types';
import { motion } from 'framer-motion';

// Custom node component
function EtymologyNode({ data, id }: { data: RootWord; id: string }) {
  const languageColor = data.language && languageColors[data.language] 
    ? languageColors[data.language].split(' ')[0] 
    : 'bg-gray-700';

  // Need to show source handles on all nodes that might have children
  // Show target handles on all nodes that might have parents
  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="bg-white p-4 rounded-lg border-2 border-gray-300 shadow-md max-w-[250px]"
    >
      {/* All nodes can be sources */}
      <Handle
        type="source"
        position={Position.Bottom}
        id="bottom"
        style={{ background: '#333', width: '8px', height: '8px' }}
      />
      
      {/* All nodes except the main one can be targets */}
      {id !== 'main' && (
        <Handle
          type="target"
          position={Position.Top}
          id="top"
          style={{ background: '#333', width: '8px', height: '8px' }}
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

export default function EtymologyFlow({ words }: { words: RootWord[] }) {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  
  // Memoize nodeTypes to prevent recreation on every render
  const nodeTypes = useMemo(() => ({ etymologyNode: EtymologyNode }), []);
  
  // Create the node structure
  useMemo(() => {
    if (!words || words.length === 0) return;
    
    const newNodes: Node[] = [];
    
    // Map to track created nodes by word text
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
    if (!nodes || nodes.length <= 1 || !words || words.length === 0) return;
    
    const newEdges: Edge[] = [];
    const wordToNodeId = new Map<string, string>();
    
    // Create mapping of word text to node id
    nodes.forEach(node => {
      wordToNodeId.set(node.data.word, node.id);
    });
    
    // Helper function to create an edge if both nodes exist
    const createEdge = (sourceWord: string, targetWord: string) => {
      const sourceId = wordToNodeId.get(sourceWord);
      const targetId = wordToNodeId.get(targetWord);
      
      if (sourceId && targetId) {
        const edgeId = `e_${sourceId}_to_${targetId}`;
        
        // Check if this edge already exists to avoid duplicates
        if (!newEdges.some(edge => edge.id === edgeId)) {
          newEdges.push({
            id: edgeId,
            source: sourceId,
            target: targetId,
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
      }
    };
    
    // Process the original data structure to build edges
    const mainWord = words[0] as EtymologyWord;
    
    // Connect main word to its etymology words (direct descendants)
    if (mainWord.etymology) {
      for (const etymWord of mainWord.etymology) {
        createEdge(mainWord.word, etymWord.word);
      }
    }
    
    // Function to connect a word to its roots recursively
    const connectRootsRecursively = (word: RootWord) => {
      if (word.roots && word.roots.length > 0) {
        for (const root of word.roots) {
          createEdge(word.word, root.word);
          
          // Recursively connect this root's roots
          connectRootsRecursively(root);
        }
      }
    };
    
    // Process each word in the flattened array
    for (const word of words) {
      connectRootsRecursively(word);
    }
    
    // Check for isolated nodes with no connections
    const connectedNodeIds = new Set<string>();
    newEdges.forEach(edge => {
      connectedNodeIds.add(edge.source);
      connectedNodeIds.add(edge.target);
    });
    
    console.log('Connected nodes:', connectedNodeIds);
    console.log('Total nodes:', nodes.length);
    console.log('Total edges:', newEdges.length);
    
    setEdges(newEdges);
  }, [nodes, words, setEdges]);
  
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