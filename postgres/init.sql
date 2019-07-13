create table if not exists users (
    uid serial not null
        constraint users_pkey
        primary key,
    vkid text not null unique
);

create table if not exists wants (
    uid integer not null,
    pid integer not null,
    unique (uid, pid)
);

create table if not exists gifts (
    uid integer not null,
    gid integer unique not null,
    unique (uid, gid)
);

-- create unique index if not exists users_vkid_idx
--     on users (vkid);
-- this index is auto-created

create index if not exists wants_uid_idx
    on wants (uid);

create index if not exists gifts_uid_idx
    on gifts (uid);

-- create unique index if not exists gifts_gid_idx
--     on gifts (gid);
-- this index is auto-created

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
