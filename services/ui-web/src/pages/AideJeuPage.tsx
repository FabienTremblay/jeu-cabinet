// src/pages/AideJeuPage.tsx
import React from "react";
import { useLocation, useNavigate } from "react-router-dom";
import PageLayout from "../components/layout/PageLayout";
import Button from "../components/shared/Button";

const AideJeuPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const retour = new URLSearchParams(location.search).get("retour");
  const cheminRetour = retour?.startsWith("/") ? retour : "/";

  return (
      <div className="aide">
        <div className="aide-entete">
          <h1>comprendre le jeu</h1>
          <button
            type="button"
            className="aide-retour"
            onClick={() => navigate(cheminRetour)}
          >
            retour
          </button>
        </div>

        {/* 1) chapeau narratif : ton texte initial */}
        <section className="aide-bloc">
          <p>
            bienvenue au cabinet : l’endroit où les bonnes intentions meurent de surcharge.
          </p>
          <p>
            votre monnaie, c’est <strong>l’attention</strong>. votre carburant, c’est le{" "}
            <strong>capital politique</strong>. votre fardeau, c’est le{" "}
            <strong>programme</strong>.
          </p>
          <p>
            entre les coups de coude internes et les crises qui tombent sans prévenir,{" "}
            <strong>l’opposition</strong> n’a pas besoin d’être brillante : elle doit juste
            vous regarder trébucher.
          </p>
          <p>
            faites passer des mesures. gardez la coalition en vie. et si possible… évitez
            de devenir le bouc émissaire du jour.
          </p>
        </section>

        {/* 2) démarrer vite */}
        <section className="aide-bloc">
          <h2>démarrer vite</h2>
          <ul>
            <li>vous jouez des cartes (mesures, influences, relations).</li>
            <li>le monde déclenche des événements (souvent injustes, parfois utiles).</li>
            <li>vous construisez un programme, puis vous votez.</li>
          </ul>
        </section>

        {/* 3) principes */}
        <section className="aide-bloc">
          <h2>principes</h2>
          <ul>
            <li>vous jouez avec une ressource rare : l’attention.</li>
            <li>chaque action coûte, et chaque coût a une lecture politique.</li>
            <li>le programme est collectif, mais les intérêts ne le sont pas.</li>
            <li>l’opposition progresse quand le cabinet s’épuise, hésite ou se déchire.</li>
          </ul>
        </section>

        {/* 4) acteurs */}
        <section className="aide-bloc">
          <h2>acteurs</h2>
          <ul>
            <li>
              <strong>le cabinet</strong> : force collective, stabilité fragile.
            </li>
            <li>
              <strong>les ministres</strong> : ambitions, rivalités, arbitrages.
            </li>
            <li>
              <strong>l’opposition</strong> : pression constante, opportunisme.
            </li>
            <li>
              <strong>le monde</strong> : crises et aléas qui ne demandent pas la permission.
            </li>
          </ul>
        </section>

        {/* 5) interface */}
        <section className="aide-bloc">
          <h2>interface</h2>
          <ul>
            <li>
              <strong>journal</strong> : ce que le système retient politiquement.
            </li>
            <li>
              <strong>bandeau</strong> : ce qui est critique maintenant.
            </li>
            <li>
              <strong>programme</strong> : ce qui est en jeu collectivement.
            </li>
            <li>
              <strong>indicateurs</strong> : ce qui s’érode, ce qui tient… et ce qui casse.
            </li>
          </ul>
        </section>

        {/* 6) subtilités */}
        <section className="aide-bloc">
          <h2>subtilités</h2>
          <p>
            si vous voulez comprendre les règles fines (attention engagée, vote, retrait,
            reset), c’est ici :
          </p>
          <div className="aide-actions">
            <Button variant="secondary" onClick={() => navigate("/aide/programme")}>
              comprendre le programme
            </Button>
          </div>
        </section>

        <section id="timeout-partie" className="aide-bloc">
          <h2>timeout d’inactivité</h2>
          <p>
            le délai d’inactivité sert à terminer automatiquement une partie qui ne reçoit
            plus d’activité pendant la durée choisie par l’hôte.
          </p>
          <ul>
            <li>le réglage est choisi dans la table avant le lancement.</li>
            <li>il s’applique à la partie au moment où l’hôte la lance.</li>
            <li>après le lancement, il ne peut plus être changé depuis le lobby.</li>
            <li>
              le timeout n’est pas un abandon joueur : il concerne l’inactivité globale de
              la partie.
            </li>
            <li>
              il ne remplace pas une fermeture normale : une partie peut aussi se terminer
              par ses règles de jeu ou par une action de fin prévue.
            </li>
          </ul>
        </section>

        {/* 7) gagner / perdre */}
        <section className="aide-bloc">
          <h2>gagner / perdre</h2>
          <p>
            on ne “gagne” pas toujours en gouvernant bien. vous gagnez en survivant
            politiquement, en imposant une trajectoire, ou en évitant l’effondrement au pire
            moment.
          </p>
        </section>

        {/* 8) note skins */}
        <section className="aide-bloc aide-note">
          <p>
            note : l’aide décrit les mécanismes “par défaut”. certains skins peuvent ajuster
            l’ordre des sous-phases ou le contenu des cartes.
          </p>
        </section>
      </div>
  );
};

export default AideJeuPage;
