-- sql/01-init-jeu.sql
-- schéma durable du service lobby

begin;

create table if not exists lobby_joueurs (
  id_joueur text primary key,
  nom text not null,
  alias text not null,
  courriel text not null unique,
  mot_de_passe_hache text not null,
  cree_le timestamptz not null default now(),
  maj_le timestamptz not null default now()
);

create table if not exists lobby_tables (
  id_table text primary key,
  nom_table text not null,
  nb_sieges int not null check (nb_sieges > 0),
  id_hote text not null references lobby_joueurs(id_joueur),
  statut text not null,
  skin_jeu text not null,
  id_partie text null,
  politique_timeout_partie jsonb not null default '{"version":1,"active":true,"delai_inactivite_secondes":3600}'::jsonb,
  cree_le timestamptz not null default now(),
  maj_le timestamptz not null default now()
);

alter table lobby_tables
  add column if not exists politique_timeout_partie jsonb
  not null default '{"version":1,"active":true,"delai_inactivite_secondes":3600}'::jsonb;

create index if not exists idx_lobby_tables_statut on lobby_tables(statut);
create index if not exists idx_lobby_tables_id_partie on lobby_tables(id_partie);

create table if not exists lobby_table_joueurs (
  id_table text not null references lobby_tables(id_table) on delete cascade,
  id_joueur text not null references lobby_joueurs(id_joueur),
  role text not null,
  assis boolean not null,
  pret boolean not null,
  primary key (id_table, id_joueur)
);

create index if not exists idx_lobby_table_joueurs_id_joueur on lobby_table_joueurs(id_joueur);

create table if not exists lobby_sessions (
  id_session text primary key,
  id_joueur text not null references lobby_joueurs(id_joueur),
  statut text not null check (statut in ('active', 'absente', 'expiree')),
  dernier_heartbeat timestamptz not null,
  expire_le timestamptz not null,
  cree_le timestamptz not null default now(),
  maj_le timestamptz not null default now()
);

create index if not exists idx_lobby_sessions_id_joueur on lobby_sessions(id_joueur);
create index if not exists idx_lobby_sessions_statut_expire on lobby_sessions(statut, expire_le);

commit;
