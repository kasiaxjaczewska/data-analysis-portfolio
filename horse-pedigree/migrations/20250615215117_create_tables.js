// dodawanie tablic
exports.up = function(knex) {
     return Promise.all([
       knex.schema.createTable('countries', table => {
         table.string('iso_code', 2).primary();
         table.string('name').notNullable();
       }),
       knex.schema.createTable('breeders', table => {
         table.increments('id').primary();
         table.string('name').notNullable();
         table.string('country_iso_code', 2).references('countries.iso_code').onDelete('CASCADE');
       }),
       knex.schema.createTable('colors', table => {
         table.increments('id').primary();
         table.string('name').notNullable();
       }),
       knex.schema.createTable('breeds', table => {
         table.string('code').primary();
         table.string('description').notNullable();
       }),
       knex.schema.createTable('horses', table => {
         table.increments('id').primary();
         table.string('name').notNullable();
         table.string('breed_code').references('breeds.code').onDelete('SET NULL');
         table.date('birth_date').notNullable();
         table.enu('gender', ['klacz', 'ogier', 'walach']).notNullable();
         table.integer('father_id').unsigned().references('horses.id').onDelete('SET NULL');
         table.integer('mother_id').unsigned().references('horses.id').onDelete('SET NULL');
         table.integer('color_id').unsigned().references('colors.id').onDelete('SET NULL');
         table.integer('breeder_id').unsigned().references('breeders.id').onDelete('SET NULL');
       }),

        // Dodanie funkcji i triggera w migracji
        knex.raw(`
          CREATE OR REPLACE FUNCTION prevent_id_update()
          RETURNS TRIGGER AS $$
          BEGIN
            IF OLD.id != NEW.id THEN
              RAISE EXCEPTION 'Update of id column is not allowed';
            END IF;
            RETURN NEW;
          END;
          $$ LANGUAGE plpgsql;
        `),
        knex.raw(`
          CREATE TRIGGER prevent_horses_id_update
          BEFORE UPDATE ON horses
          FOR EACH ROW
          EXECUTE FUNCTION prevent_id_update();
        `)
     ]);
   };

   // usuwanie tablic
   exports.down = function(knex) {
     return Promise.all([
       knex.schema.dropTableIfExists('horses'),
       knex.schema.dropTableIfExists('colors'),
       knex.schema.dropTableIfExists('breeds'),
       knex.schema.dropTableIfExists('breeders'),
       knex.schema.dropTableIfExists('countries')
     ]);
   };