-- Migration 001 : sessions jetables du lobby.

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
