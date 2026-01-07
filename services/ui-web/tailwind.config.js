// tailwind.config.js
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{ts,tsx,js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Palette principale
        bleuGlacier: "#4BA3FF",
        bleuBoreal: "#1E3A5F",
        blancNordique: "#F4F7FA",
        grisBeton: "#5F6A73",
        grisBrouillard: "#E0E6EC",

        // Accents
        rougeErable: "#C72E2E",
        bleuMinistre: "#0074DA",
      },
      fontFamily: {
        // à relier à Neue Haas Grotesk via @font-face si tu l’ajoutes
        titre: ['"Neue Haas Grotesk"', "Montserrat", "system-ui", "sans-serif"],
        corps: ['"Public Sans"', "system-ui", "sans-serif"],
      },
      boxShadow: {
        carte: "0 2px 6px rgba(0,0,0,0.08)",
        modal: "0 4px 12px rgba(0,0,0,0.12)",
      },
      borderRadius: {
        card: "6px",
      },
    },
  },
  plugins: [],
};
