import dynamic from 'next/dynamic';

const DynamicMonaco = dynamic(() => import('@monaco-editor/react'), { ssr: false });

export default DynamicMonaco;
