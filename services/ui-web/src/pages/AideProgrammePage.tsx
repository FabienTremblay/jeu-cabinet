// src/pages/AideProgrammePage.tsx
import React from "react";

const AideProgrammePage: React.FC = () => {
  return (
    <div className="aide">
      <h1>programme — règles fines</h1>

      <section className="aide-bloc">
        <p>
          le programme est une liste de cartes engagées pour le tour en cours. chaque entrée
          consomme de l’attention et doit survivre à un vote.
        </p>
      </section>

      <section className="aide-bloc">
        <h2>engager une carte</h2>
        <ul>
          <li>la carte est retirée de la main du joueur.</li>
          <li>son coût en attention est immédiatement débité.</li>
          <li>l’entrée mémorise l’attention engagée.</li>
        </ul>
      </section>

      <section className="aide-bloc">
        <h2>voter</h2>
        <ul>
          <li>chaque joueur dispose d’un vote.</li>
          <li>le vote est enregistré par joueur.</li>
          <li>un programme incomplet ou instable peut être rejeté.</li>
        </ul>
      </section>

      <section className="aide-bloc">
        <h2>retirer une carte</h2>
        <ul>
          <li>la carte revient dans la main de son auteur.</li>
          <li>l’attention engagée est remboursée.</li>
        </ul>
      </section>

      <section className="aide-bloc">
        <h2>résolution du programme : exécution & points</h2>
        <p>
          quand le programme est résolu, le moteur exécute les cartes une par une, puis distribue
          les points selon les contributions.
        </p>

        <h3>si le programme est vide</h3>
        <ul>
          <li>aucune carte n’est exécutée</li>
          <li><strong>0 point</strong> (ni individuel, ni collectif)</li>
        </ul>

        <h3>si le programme contient des cartes</h3>
        <ul>
          <li>
            <strong>pour chaque carte exécutée</strong> : l’auteur gagne{" "}
            <strong>+1 capital politique individuel</strong>.
          </li>
          <li>
            <strong>au total</strong> : le cabinet gagne{" "}
            <strong>+1 capital collectif</strong> par carte exécutée.
          </li>
          <li>
            ensuite, le programme est <strong>réinitialisé</strong> (les cartes sont consommées et
            défaussées).
          </li>
        </ul>

        <h3>exemple</h3>
        <ul>
          <li>programme : 5 cartes</li>
          <li>joueur A en a proposé 3 → <strong>+3</strong> capital individuel</li>
          <li>joueur B en a proposé 2 → <strong>+2</strong> capital individuel</li>
          <li>cabinet → <strong>+5</strong> capital collectif</li>
        </ul>

      </section>

      <section className="aide-bloc">
        <h2>rejeter un programme ou réinitialiser</h2>
        <ul>
          <li>
            <strong>rejeter</strong> : tout est annulé, rien n’est consommé.
          </li>
        </ul>
      </section>
    </div>
  );
};

export default AideProgrammePage;

