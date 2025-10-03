import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import FloodMap from './component/Floodmap'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <FloodMap/>
    </>
  )
}

export default App
