import { createGlobalStyle } from 'styled-components';

const GlobalStyles = createGlobalStyle`
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@400;500;600;700&display=swap');

  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  html {
    scroll-behavior: smooth;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }

  body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
    background-color: #F9F3E5; /* Cream color */
    color: #5E4E3E; /* Taupe color */
    line-height: 1.6;
    min-height: 100vh;
    overflow-x: hidden;
  }

  h1, h2, h3, h4, h5, h6 {
    font-family: 'Playfair Display', Georgia, serif;
    font-weight: 600;
    color: #5E4E3E; /* Taupe color */
    margin-bottom: 1rem;
  }

  a {
    color: #8B9474; /* Sage color */
    text-decoration: none;
    transition: color 0.3s ease;

    &:hover {
      color: #737A5F; /* Darker sage */
    }
  }

  button {
    cursor: pointer;
    font-family: 'Inter', sans-serif;
  }

  /* Custom scrollbar */
  ::-webkit-scrollbar {
    width: 10px;
  }

  ::-webkit-scrollbar-track {
    background: #F9F3E5; /* Cream color */
  }

  ::-webkit-scrollbar-thumb {
    background: #8B735B; /* Brown color */
    border-radius: 5px;

    &:hover {
      background: #735E4A; /* Darker brown */
    }
  }

  /* Selection color */
  ::selection {
    background-color: rgba(139, 148, 116, 0.3); /* Sage with opacity */
    color: #5E4E3E; /* Taupe color */
  }

  /* Utility classes */
  .text-cream { color: #F9F3E5; }
  .text-brown { color: #8B735B; }
  .text-peach { color: #E8C9AC; }
  .text-sage { color: #8B9474; }
  .text-taupe { color: #5E4E3E; }

  .bg-cream { background-color: #F9F3E5; }
  .bg-brown { background-color: #8B735B; }
  .bg-peach { background-color: #E8C9AC; }
  .bg-sage { background-color: #8B9474; }
  .bg-taupe { background-color: #5E4E3E; }

  /* Layout utilities */
  .container {
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
  }

  .section-padding {
    padding: 80px 0;
  }

  .shadow-natural {
    box-shadow: 0 10px 40px rgba(139, 116, 91, 0.1);
  }

  .gradient-natural {
    background: linear-gradient(135deg, #F9F3E5 0%, #E8C9AC 100%);
  }

  .gradient-earthy {
    background: linear-gradient(135deg, #8B735B 0%, #5E4E3E 100%);
  }
`;

export default GlobalStyles;