(self.webpackChunk_N_E=self.webpackChunk_N_E||[]).push([[974],{721:(e,t,o)=>{"use strict";o.r(t),o.d(t,{default:()=>b});var a=o(5155),l=o(2115),n=o(8200);function r(e){let{onSearch:t,compact:o=!1}=e,[r,s]=(0,l.useState)(""),i=e=>{e.preventDefault(),r.trim()&&t(r.trim())};return o?(0,a.jsx)("form",{onSubmit:i,className:"w-full",children:(0,a.jsxs)("div",{className:"relative",children:[(0,a.jsx)("input",{type:"text",value:r,onChange:e=>s(e.target.value),placeholder:"Search...",className:"w-full rounded text-sm p-1 pl-7 pr-16 border border-gray-200"}),(0,a.jsx)(n.A,{className:"absolute left-2 top-1.5 text-gray-400",size:14}),(0,a.jsx)("button",{type:"submit",className:"absolute right-1 top-1 rounded bg-blue-500 text-white px-2 py-0.5 text-xs",disabled:!r.trim(),children:"Search"})]})}):(0,a.jsx)("form",{onSubmit:i,children:(0,a.jsxs)("div",{className:"relative",children:[(0,a.jsx)("input",{type:"text",value:r,onChange:e=>s(e.target.value),placeholder:"Search for a word...",className:"w-full rounded-lg bg-zinc-800 p-4 pl-12 border border-zinc-600 text-white"}),(0,a.jsx)(n.A,{className:"absolute left-4 top-4 text-zinc-400",size:20}),(0,a.jsx)("button",{type:"submit",className:"absolute right-2 top-2 rounded bg-zinc-700 px-4 py-2 text-white",disabled:!r.trim(),children:"Search"})]})})}var s=o(4211);o(1687);let i={English:"bg-etymology-blue text-white",Latin:"bg-etymology-purple text-white",Greek:"bg-etymology-red text-white",French:"bg-etymology-yellow text-black",German:"bg-etymology-green text-white",default:"bg-gray-700 text-white"};var c=o(470);function d(e){let{data:t,id:o}=e,l=t.language&&i[t.language]?i[t.language].split(" ")[0]:"bg-gray-700";return(0,a.jsxs)(c.P.div,{initial:{opacity:0},animate:{opacity:1},className:"bg-white p-4 rounded-lg border-2 border-gray-300 shadow-md max-w-[250px]",children:[(0,a.jsx)(s.h7,{type:"source",position:s.yX.Bottom,id:"bottom",style:{background:"#333",width:"8px",height:"8px"}}),"main"!==o&&(0,a.jsx)(s.h7,{type:"target",position:s.yX.Top,id:"top",style:{background:"#333",width:"8px",height:"8px"}}),(0,a.jsx)("h3",{className:"text-lg font-bold text-gray-800 mb-1",children:t.word}),(0,a.jsx)("span",{className:"inline-block rounded-full px-2 py-0.5 text-xs text-white ".concat(l," mb-2"),children:t.language}),t.definition&&(0,a.jsx)("p",{className:"text-sm text-gray-600 mb-2",children:t.definition}),t.year&&(0,a.jsx)("div",{className:"text-xs text-gray-500",children:t.year>0?t.year:t.year<0?"".concat(Math.abs(t.year)," BCE"):"unknown"})]})}function g(e){let{words:t}=e,[o,n,r]=(0,s.ck)([]),[i,c,g]=(0,s.fM)([]),[u,h]=(0,l.useState)(new Map),[f,y]=(0,l.useState)(new Map),m=(0,l.useMemo)(()=>({etymologyNode:d}),[]);return((0,l.useMemo)(()=>{if(!t||0===t.length)return;let e=[],o=new Map,a=(()=>{let e=t[0],o=new Map;t.forEach(e=>{o.set(e.word,e)});let a=(e,t)=>{let o={...e,children:[],depth:t};if(0===t&&e.etymology){let l=e.etymology;if(l)for(let e of l)o.children.push(a(e,t+1))}if(e.roots)for(let l of e.roots)o.children.push(a(l,t+1));return o};return a(e,0)})();(t=>{t.forEach((t,a)=>{let l=-((t.length-1)*250)/2;t.forEach((t,n)=>{let r=0===a?"main":"".concat(t.word,"_").concat(a,"_").concat(n),s=l+250*n;e.push({id:r,type:"etymologyNode",position:{x:s,y:200*a},data:t}),o.set(t.word,r)})})})((e=>{let t=new Map,o=e=>{t.has(e.depth)||t.set(e.depth,[]);let a=t.get(e.depth);for(let t of(a&&a.push(e),e.children))o(t)};return o(e),t.forEach(e=>{e.forEach((e,t)=>{e.index=t})}),t})(a));let l=(e,t)=>{for(let o of e.children)t.set(o.word,e.word),l(o,t)},r=new Map;l(a,r),console.log("Parent-child map:",Object.fromEntries(r)),console.log("Node map:",Object.fromEntries(o)),n(e),h(r),y(o)},[t,n]),(0,l.useMemo)(()=>{if(!o||o.length<=1||!u.size||!f.size)return;let e=[];u.forEach((t,o)=>{let a=f.get(t),l=f.get(o);if(a&&l){let t="e_".concat(a,"_to_").concat(l);e.some(e=>e.id===t)||e.push({id:t,source:a,target:l,sourceHandle:"bottom",targetHandle:"top",type:"default",animated:!1,markerEnd:{type:s.TG.Arrow,color:"#333",width:15,height:15},style:{stroke:"#333",strokeWidth:2,opacity:1}})}}),console.log("Created edges:",e.length),c(e)},[o,u,f,c]),t&&0!==t.length)?(0,a.jsx)(s.Gc,{nodes:o,edges:i,onNodesChange:r,onEdgesChange:g,nodeTypes:m,elevateEdgesOnSelect:!0,elevateNodesOnSelect:!1,fitView:!0,fitViewOptions:{padding:.3},defaultEdgeOptions:{type:"default",animated:!1,style:{stroke:"#333",strokeWidth:2,opacity:.8}},style:{background:"rgb(245, 245, 245)",width:"100%",height:"100%"},proOptions:{hideAttribution:!1},className:"h-full w-full"}):(0,a.jsx)("div",{className:"flex h-full items-center justify-center",children:"No etymology data available"})}function u(e){let{words:t}=e,o=t.filter(e=>null!=e.year).sort((e,t)=>e.year-t.year);if(o.length<=1)return(0,a.jsx)("div",{className:"text-center text-xs text-gray-500",children:"Not enough dated words"});let l=o.map(e=>e.year),n=Math.min(...l),r=Math.max(...l),s=r-n;return(0,a.jsxs)("div",{className:"w-full",children:[(0,a.jsxs)("div",{className:"flex justify-between text-xs mb-1",children:[(0,a.jsx)("span",{className:"font-medium",children:"Timeline"}),(0,a.jsxs)("span",{className:"text-gray-500",children:[n<0?"".concat(Math.abs(n)," BCE"):n," — ",r<0?"".concat(Math.abs(r)," BCE"):r]})]}),(0,a.jsxs)("div",{className:"relative h-6",children:[(0,a.jsx)("div",{className:"absolute left-0 right-0 top-1/2 h-0.5 bg-gray-200"}),o.map((e,t)=>{let o=e.year,l=(o-n)/s*100,r=e.language&&i[e.language]?i[e.language].split(" ")[0]:"bg-gray-700";return(0,a.jsx)("div",{className:"absolute",style:{left:"".concat(l,"%"),top:"50%",transform:"translate(-50%, -50%)"},title:"".concat(e.word," (").concat(o<0?"".concat(Math.abs(o)," BCE"):o,")"),children:(0,a.jsx)("div",{className:"h-2 w-2 ".concat(r," rounded-full")})},"word-".concat(t))})]})]})}var h=o(8075);let f="Ponchia",y="etymology-website",m="data/words",p=new h.Eg,w={etymology:{word:"etymology",language:"English",year:1398,definition:"the study of the origin and history of words",etymology:[{word:"etymologia",language:"Latin",year:1350}],roots:[{word:"etymologia",language:"Latin",definition:"origin of words",year:1350,roots:[{word:"etymon",language:"Greek",definition:"true sense",year:null,roots:[{word:"etymos",language:"Greek",definition:"true, real, actual",year:null}]},{word:"logia",language:"Greek",definition:"study of",year:null,roots:[{word:"logos",language:"Greek",definition:"word, speech, discourse, reason",year:null}]}]}]},philosophy:{word:"philosophy",language:"English",year:1340,definition:"love or pursuit of wisdom; systematic investigation of the nature of truth",etymology:[{word:"philosophie",language:"French",year:1290,definition:"love of wisdom"}],roots:[{word:"philosophia",language:"Latin",definition:"the study of philosophy",year:null,roots:[{word:"philosophos",language:"Greek",definition:"lover of wisdom",year:null,roots:[{word:"philos",language:"Greek",definition:"loving, dear",year:null},{word:"sophia",language:"Greek",definition:"knowledge, wisdom",year:null,roots:[{word:"sophos",language:"Greek",definition:"wise",year:null}]}]}]}]},monde:{word:"monde",language:"French",year:1050,definition:"world, universe, earth",etymology:[],roots:[{word:"mundus",language:"Latin",definition:"world, universe, the heavens",year:null,roots:[{word:"mundus",language:"Latin",definition:"clean, elegant",year:null,roots:[{word:"munde",language:"Latin",definition:"cleanly, neatly",year:null}]}]}]},amor:{word:"amor",language:"Latin",year:-100,definition:"love, affection, passion",etymology:[],roots:[{word:"ama",language:"Proto-Italic",definition:"love",year:null,roots:[{word:"am-",language:"Proto-Indo-European",definition:"mother, nurse",year:null}]}]},polis:{word:"polis",language:"Greek",year:-800,definition:"city, city-state",etymology:[],roots:[{word:"pele-",language:"Proto-Indo-European",definition:"citadel, fortified high place",year:null}]}};async function x(e){try{let t=e.toLowerCase().trim();console.log("Attempting to fetch from GitHub");try{let e="https://raw.githubusercontent.com/".concat(f,"/").concat(y,"/main/").concat(m,"/English/").concat(t.charAt(0).toLowerCase(),"/").concat(t,".json");try{console.log("Trying raw GitHub URL: ".concat(e));let t=await fetch(e);if(t.ok){let e=await t.json();return console.log("Successfully fetched from raw GitHub URL"),e}}catch(e){console.log("Error fetching from raw GitHub URL, trying API instead:",e)}for(let e of["English","French","Latin","Greek"]){let o="https://raw.githubusercontent.com/".concat(f,"/").concat(y,"/main/").concat(m,"/").concat(e,"/").concat(t.charAt(0).toLowerCase(),"/").concat(t,".json");try{console.log("Trying language-specific raw URL: ".concat(o));let t=await fetch(o);if(t.ok){let o=await t.json();return console.log("Successfully fetched from ".concat(e," directory")),o}}catch(t){console.log("Error fetching from ".concat(e," directory"))}}for(let e of(console.log("Falling back to GitHub API"),["English","French","Latin","Greek"])){let o="".concat(m,"/").concat(e,"/").concat(t.charAt(0).toLowerCase(),"/").concat(t,".json");try{console.log("Trying GitHub API with path: ".concat(o));let t=await p.rest.repos.getContent({owner:f,repo:y,path:o});if(200===t.status&&"content"in t.data){let o=atob(t.data.content);return console.log("Successfully fetched from GitHub API (".concat(e," directory)")),JSON.parse(o)}}catch(t){console.log("Error fetching from GitHub API (".concat(e," directory)"))}}if(console.log("All GitHub fetch attempts failed, checking for fallback data"),w[t])return console.log('Falling back to sample data for "'.concat(t,'"')),w[t];return null}catch(e){if(console.error("Error in GitHub fetch logic:",e),w[t])return console.log('Falling back to sample data for "'.concat(t,'"')),w[t];return null}}catch(e){return console.error("Error in getWordEtymology:",e),null}}function b(){let[e,t]=(0,l.useState)(!1),[o,n]=(0,l.useState)(null),[s,i]=(0,l.useState)(null),[c,d]=(0,l.useState)(null),[h,f]=(0,l.useState)([]),y=async e=>{t(!0),n(null),i(e);try{let t=await x(e);if(t){d(t);let e=function(e){let t=[];if(t.push(e),e.etymology&&e.etymology.length>0)for(let o of e.etymology)t.push(o);let o=function(e){let a=arguments.length>1&&void 0!==arguments[1]?arguments[1]:0;if(e.roots&&e.roots.length>0)for(let l of e.roots)t.push(l),o(l,a+1)};if(e.roots&&e.roots.length>0)for(let a of e.roots)t.push(a),o(a);return t}(t);f(e)}else n('No etymology data found for "'.concat(e,'"')),d(null),f([])}catch(e){n("Error: ".concat(e instanceof Error?e.message:String(e))),d(null),f([])}finally{t(!1)}};return c||e||o?e?(0,a.jsxs)("div",{className:"full-page",children:[(0,a.jsx)("div",{className:"animate-spin h-10 w-10 border-4 border-blue-500 border-t-transparent rounded-full"}),(0,a.jsx)("p",{className:"mt-4",children:"Loading..."})]}):o?(0,a.jsxs)("div",{className:"full-page",children:[(0,a.jsx)("div",{className:"bg-red-50 text-red-800 p-4 rounded-lg max-w-md",children:o}),(0,a.jsx)("button",{onClick:()=>{n(null),i(null)},className:"mt-4 bg-blue-500 text-white px-4 py-2 rounded",children:"Try Again"})]}):(0,a.jsxs)("div",{className:"h-screen flex flex-col",children:[(0,a.jsxs)("div",{className:"bg-white/90 p-3 shadow-sm flex justify-between items-center",children:[(0,a.jsxs)("h1",{className:"font-bold",children:["Etymology of ",(0,a.jsx)("span",{className:"italic",children:s})]}),(0,a.jsx)("div",{className:"w-64",children:(0,a.jsx)(r,{onSearch:y,compact:!0})})]}),(0,a.jsx)("div",{className:"flex-1 flow-container",children:(0,a.jsx)(g,{words:h})}),(0,a.jsx)("div",{className:"bg-white/90 p-2 border-t",children:(0,a.jsx)(u,{words:h})})]}):(0,a.jsxs)("div",{className:"full-page",children:[(0,a.jsx)("h1",{className:"text-4xl font-bold mb-2",children:"Etymology Explorer"}),(0,a.jsx)("p",{className:"text-zinc-400 mb-8",children:"Discover the origins and history of words"}),(0,a.jsx)("div",{className:"w-full max-w-md",children:(0,a.jsx)(r,{onSearch:y})})]})}},9426:(e,t,o)=>{Promise.resolve().then(o.bind(o,721))}},e=>{var t=t=>e(e.s=t);e.O(0,[294,702,255,441,684,358],()=>t(9426)),_N_E=e.O()}]);