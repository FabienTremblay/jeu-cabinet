import React from "react";

const PrincipesPage: React.FC = () => {
  return (
    <div className="max-w-2xl space-y-4">
      <h1 className="text-xl font-semibold">principes</h1>

      <section className="space-y-2 text-sm opacity-90">
        <ul className="list-disc pl-5 space-y-1">
          <li>vous manquez toujours de temps : l’attention est votre vraie monnaie.</li>
          <li>tout gain a un coût politique : sauver le collectif peut ruiner l’individuel (et inversement).</li>
          <li>la stabilité est un mirage : les événements mondiaux forcent l’improvisation.</li>
          <li>la coordination est difficile : le cabinet n’est pas une équipe, c’est une cohabitation.</li>
        </ul>
      </section>

      <section className="space-y-2 text-xs opacity-80">
        <p>
          si tu veux ajouter des principes “plus narratifs” (ton cabinet, ton univers),
          on peut les mettre ici sans toucher au moteur.
        </p>
      </section>
    </div>
  );
};

export default PrincipesPage;
