const { Pool } = require('pg');
const types = require('pg').types;

// Parsowanie typu DATE (OID 1082) jako string w formacie YYYY-MM-DD
types.setTypeParser(1082, value => value);

module.exports = {
  development: {
    client: 'pg',
    connection: {
      host: 'localhost',
      user: 'horse_user',
      password: 'Mandarynka242',
      database: 'horse_pedigree'
    },
    pool: {
      min: 0,
      max: 7
    },
    migrations: {
      tableName: 'knex_migrations'
    },
    seeds: {
      directory: './seeds'
    }
  }
};
