create table if not exists users (
    uid serial not null
        constraint users_pkey
        primary key,
    vkid text not null unique,
    wishes boolean not null default false
);

create table if not exists wants (
    uid integer not null,
    pid integer not null,
    gid integer default null,
    unique (uid, pid),
    unique (uid, pid, gid)
);

create table if not exists friends (
    uid integer not null references users,
    fid integer not null references users,
    unique (uid, fid)
);

create index if not exists friends_uid_idx
    on friends (uid);

create index if not exists wants_uid_idx
    on wants (uid);

create index if not exists wants_gid_idx
    on wants (gid);

create table if not exists popular (
    pid integer not null
        constraint popular_pkey
        primary key,
    rate integer not null default 0
);

CREATE OR REPLACE FUNCTION update_popular() RETURNS TRIGGER AS $update_popular_t$
    BEGIN
        IF (TG_OP = 'INSERT') THEN
            INSERT INTO popular (pid, rate) values (new.pid, 0)
                ON CONFLICT (pid) do nothing;
             UPDATE popular set rate = rate + 1 where pid = new.pid;
            RETURN new;
        ELSIF (TG_OP = 'DELETE') THEN
            UPDATE popular set rate = rate - 1 where pid = old.pid;
            RETURN old;
        END IF;
        RETURN NULL; -- result is ignored since this is an AFTER trigger
    END;
$update_popular_t$ LANGUAGE plpgsql;

drop trigger if exists update_popular_t
    on wants;

CREATE TRIGGER update_popular_t
AFTER INSERT OR DELETE ON wants
    FOR EACH ROW EXECUTE PROCEDURE update_popular();
