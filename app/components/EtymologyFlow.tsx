'use client';

import React, { useMemo, useState } from 'react';
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
  
  // Move state declarations here, before they're used
  const [parentChildMap, setParentChildMap] = useState<Map<string, string>>(new Map());
  const [nodeIdMap, setNodeIdMap] = useState<Map<string, string>>(new Map());
  
  // Memoize nodeTypes to prevent recreation on every render
  const nodeTypes = useMemo(() => ({ etymologyNode: EtymologyNode }), []);
  
  // Create the node structure
  useMemo(() => {
    if (!words || words.length === 0) return;
    
    const newNodes: Node[] = [];
    
    // Map to track created nodes by word text
    const nodeMap = new Map<string, string>();
    
    // Build a hierarchical representation of the data
    interface HierarchicalWord extends RootWord {
      children: HierarchicalWord[];
      depth: number; // How deep in the tree
      index?: number; // Horizontal position at its depth level
    }
    
    // Function to build the hierarchical tree
    const buildHierarchy = (): HierarchicalWord => {
      const mainWord = words[0] as EtymologyWord;
      
      // Create a map for quick lookup of words by their text
      const wordMap = new Map<string, RootWord>();
      words.forEach(word => {
        wordMap.set(word.word, word);
      });
      
      // Recursive function to build the tree
      const buildSubtree = (word: RootWord, depth: number): HierarchicalWord => {
        const hierarchicalWord: HierarchicalWord = {
          ...word,
          children: [],
          depth
        };
        
        // Check if this is the main word with etymology
        if (depth === 0 && (word as EtymologyWord).etymology) {
          const etymology = (word as EtymologyWord).etymology;
          if (etymology) {
            for (const etymWord of etymology) {
              hierarchicalWord.children.push(buildSubtree(etymWord, depth + 1));
            }
          }
        }
        
        // Add the roots
        if (word.roots) {
          for (const rootWord of word.roots) {
            hierarchicalWord.children.push(buildSubtree(rootWord, depth + 1));
          }
        }
        
        return hierarchicalWord;
      };
      
      return buildSubtree(mainWord, 0);
    };
    
    const hierarchicalTree = buildHierarchy();
    
    // Function to assign horizontal positions at each depth level
    const assignIndices = (tree: HierarchicalWord) => {
      // Group words by depth
      const depthMap = new Map<number, HierarchicalWord[]>();
      
      // Recursive function to collect words at each depth
      const collectByDepth = (node: HierarchicalWord) => {
        if (!depthMap.has(node.depth)) {
          depthMap.set(node.depth, []);
        }
        const depthNodes = depthMap.get(node.depth);
        if (depthNodes) {
          depthNodes.push(node);
        }
        
        for (const child of node.children) {
          collectByDepth(child);
        }
      };
      
      collectByDepth(tree);
      
      // Assign indices at each depth level
      depthMap.forEach((nodesAtDepth) => {
        nodesAtDepth.forEach((node, index) => {
          node.index = index;
        });
      });
      
      return depthMap;
    };
    
    const depthMap = assignIndices(hierarchicalTree);
    
    // Calculate node positions based on depth and index
    const VERTICAL_SPACE = 200;
    const HORIZONTAL_SPACE = 250;
    
    // Function to create nodes for the flow diagram
    const createNodes = (depthMap: Map<number, HierarchicalWord[]>) => {
      // Process each depth level
      depthMap.forEach((nodesAtDepth, depth) => {
        // Calculate total width needed for this row
        const totalWidth = (nodesAtDepth.length - 1) * HORIZONTAL_SPACE;
        const startX = -totalWidth / 2;
        
        // Create nodes for this depth
        nodesAtDepth.forEach((word, index) => {
          const nodeId = depth === 0 ? 'main' : `${word.word}_${depth}_${index}`;
          const x = startX + index * HORIZONTAL_SPACE;
          const y = depth * VERTICAL_SPACE;
          
          newNodes.push({
            id: nodeId,
            type: 'etymologyNode',
            position: { x, y },
            data: word
          });
          
          nodeMap.set(word.word, nodeId);
        });
      });
    };
    
    createNodes(depthMap);
    
    // Flatten the hierarchy to help with edge creation
    const flattenHierarchy = (
      root: HierarchicalWord, 
      parentWordMap: Map<string, string>
    ) => {
      for (const child of root.children) {
        parentWordMap.set(child.word, root.word);
        flattenHierarchy(child, parentWordMap);
      }
    };
    
    // Map to track parent-child relationships
    const parentWordMap = new Map<string, string>();
    flattenHierarchy(hierarchicalTree, parentWordMap);
    
    console.log('Parent-child map:', Object.fromEntries(parentWordMap));
    console.log('Node map:', Object.fromEntries(nodeMap));
    
    setNodes(newNodes);
    
    // Store the parent-child relationships and node map as component state
    // so it can be used in the edge creation
    setParentChildMap(parentWordMap);
    setNodeIdMap(nodeMap);
    
  }, [words, setNodes]);
  
  // Create edges separately after nodes and maps are set
  useMemo(() => {
    if (!nodes || nodes.length <= 1 || !parentChildMap.size || !nodeIdMap.size) return;
    
    const newEdges: Edge[] = [];
    
    // Create edges based on parent-child relationships
    parentChildMap.forEach((parentWord, childWord) => {
      const sourceId = nodeIdMap.get(parentWord);
      const targetId = nodeIdMap.get(childWord);
      
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
    });
    
    console.log('Created edges:', newEdges.length);
    
    setEdges(newEdges);
  }, [nodes, parentChildMap, nodeIdMap, setEdges]);
  
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