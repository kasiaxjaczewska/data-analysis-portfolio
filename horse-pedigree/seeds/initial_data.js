exports.seed = async function (knex) {
  // Czyszczenie istniejacych danych
  await knex('horses').del();
  await knex('breeders').del();
  await knex('colors').del();
  await knex('breeds').del();
  await knex('countries').del();

  // Resetowanie sekwencji dla colors i breeders
  await knex.raw('ALTER SEQUENCE colors_id_seq RESTART WITH 1');
  await knex.raw('ALTER SEQUENCE breeders_id_seq RESTART WITH 1');
  await knex.raw('ALTER SEQUENCE horses_id_seq RESTART WITH 1');

  // Wstawianie krajow
  await knex('countries').insert([
    { iso_code: 'PL', name: 'Polska' },
    { iso_code: 'DE', name: 'Niemcy' },
    { iso_code: 'IT', name: 'Wlochy' },
    { iso_code: 'US', name: 'Stany Zjednoczone' },
    { iso_code: 'FR', name: 'Francja' },
    { iso_code: 'SE', name: 'Szwecja' },
    { iso_code: 'NO', name: 'Norwegia' },
    { iso_code: 'ES', name: 'Hiszpania' },
    { iso_code: 'GB', name: 'Wielka Brytania' },
    { iso_code: 'RU', name: 'Rosja' },
    { iso_code: 'JP', name: 'Japonia' },
    { iso_code: 'CN', name: 'Chiny' },
    { iso_code: 'AU', name: 'Australia' },
    { iso_code: 'CA', name: 'Kanada' },
    { iso_code: 'BR', name: 'Brazylia' },
  ]).onConflict('iso_code').ignore();

  // Wstawianie hodowcow z jawnymi ID
  await knex('breeders').insert([
    { name: 'Hodowla Koni Polskich', country_iso_code: 'PL' },
    { name: 'Stajnia Mazury', country_iso_code: 'PL' },
    { name: 'Hodowla Koni Niemieckich', country_iso_code: 'DE' },
    { name: 'Stajnia Berlin', country_iso_code: 'DE' },
    { name: 'Hodowla Koni Wloskich', country_iso_code: 'IT' },
    { name: 'Stajnia Toskanska', country_iso_code: 'IT' },
    { name: 'Hodowla Koni Amerykanskich', country_iso_code: 'US' },
    { name: 'Stajnia Teksanska', country_iso_code: 'US' },
    { name: 'Hodowla Koni Francuskich', country_iso_code: 'FR' },
    { name: 'Stajnia Normandska', country_iso_code: 'FR' },
    { name: 'Hodowla Koni Szwedzkich', country_iso_code: 'SE' },
    { name: 'Hodowla Koni Norweskich', country_iso_code: 'NO' },
    { name: 'Hodowla Koni Hiszpanskich', country_iso_code: 'ES' },
    { name: 'Hodowla Koni Brytyjskich', country_iso_code: 'GB' },
    { name: 'Hodowla Koni Rosyjskich', country_iso_code: 'RU' },
    { name: 'Hodowla Koni Japonskich', country_iso_code: 'JP' },
    { name: 'Hodowla Koni Chińskich', country_iso_code: 'CN' },
    { name: 'Hodowla Koni Australijskich', country_iso_code: 'AU' },
    { name: 'Hodowla Koni Kanadyjskich', country_iso_code: 'CA' },
    { name: 'Hodowla Koni Brazylijskich', country_iso_code: 'BR' },
  ]).onConflict('id').merge();

  // Pobieranie ID hodowcow
  const breeders = await knex('breeders').select('id', 'name');
  const breederMap = breeders.reduce((map, breeder) => {
    map[breeder.name] = breeder.id;
    return map;
  }, {});

  // Wstawianie maści z jawnymi ID
  await knex('colors').insert([
    { name: 'gniady' },
    { name: 'kasztanowy' },
    { name: 'siwy' },
    { name: 'czarny' },
    { name: 'bulany' },
  ]).onConflict('id').merge();

  // Pobieranie ID maści
  const colors = await knex('colors').select('id', 'name');
  const colorMap = colors.reduce((map, color) => {
    map[color.name] = color.id;
    return map;
  }, {});

  // Wstawianie ras
  await knex('breeds').insert([
    { code: 'oo', description: 'Rasa czysta, dzecko rodzicow ras: oo' },
    { code: 'xx', description: 'Rasa czysta, dzecko rodzicow ras: oo' },
    { code: 'xo', description: 'Rasa mieszana, dziecko rodzicow ras: oo oraz xo lub xx oraz xo' },
    { code: 'xxoo', description: 'Rasa mieszana, dziecko rodzicow ras: oo oraz xx lub xx oraz xxoo' },
  ]).onConflict('code').ignore();

  // Wstawianie koni z dynamicznymi color_id i breeder_id
  const horses = [
    { name: 'Bucefal', breed_code: 'oo', birth_date: '2015-03-10', gender: 'ogier', color_id: colorMap['gniady'], breeder_id: breederMap['Hodowla Koni Polskich'] },
    { name: 'Kleopatra', breed_code: 'oo', birth_date: '2016-05-12', gender: 'klacz', color_id: colorMap['kasztanowy'], breeder_id: breederMap['Stajnia Mazury'] },
    { name: 'Thor', breed_code: 'xx', birth_date: '2014-07-15', gender: 'ogier', color_id: colorMap['siwy'], breeder_id: breederMap['Hodowla Koni Niemieckich'] },
    { name: 'Luna', breed_code: 'xx', birth_date: '2015-09-20', gender: 'klacz', color_id: colorMap['czarny'], breeder_id: breederMap['Stajnia Berlin'] },
    { name: 'Apollo', breed_code: 'xo', birth_date: '2013-11-05', gender: 'ogier', color_id: colorMap['bulany'], breeder_id: breederMap['Hodowla Koni Wloskich'] },
    { name: 'Atena', breed_code: 'xo', birth_date: '2014-01-25', gender: 'klacz', color_id: colorMap['gniady'], breeder_id: breederMap['Stajnia Toskanska'] },
    { name: 'Herkules', breed_code: 'xxoo', birth_date: '2012-04-30', gender: 'ogier', color_id: colorMap['kasztanowy'], breeder_id: breederMap['Hodowla Koni Amerykanskich'] },
    { name: 'Afrodyta', breed_code: 'xxoo', birth_date: '2013-06-18', gender: 'klacz', color_id: colorMap['siwy'], breeder_id: breederMap['Stajnia Teksanska'] },
    { name: 'Ares', breed_code: 'oo', birth_date: '2018-02-14', gender: 'ogier', color_id: colorMap['czarny'], breeder_id: breederMap['Hodowla Koni Polskich'], father_id: null, mother_id: null },
    { name: 'Diana', breed_code: 'oo', birth_date: '2018-04-22', gender: 'klacz', color_id: colorMap['bulany'], breeder_id: breederMap['Stajnia Mazury'], father_id: null, mother_id: null },
    { name: 'Zeus', breed_code: 'xx', birth_date: '2017-08-10', gender: 'ogier', color_id: colorMap['gniady'], breeder_id: breederMap['Hodowla Koni Niemieckich'], father_id: null, mother_id: null },
    { name: 'Hera', breed_code: 'xx', birth_date: '2017-10-05', gender: 'klacz', color_id: colorMap['kasztanowy'], breeder_id: breederMap['Stajnia Berlin'], father_id: null, mother_id: null },
    { name: 'Posejdon', breed_code: 'xo', birth_date: '2019-03-15', gender: 'ogier', color_id: colorMap['siwy'], breeder_id: breederMap['Hodowla Koni Wloskich'], father_id: null, mother_id: null },
    { name: 'Demeter', breed_code: 'xo', birth_date: '2019-05-20', gender: 'klacz', color_id: colorMap['czarny'], breeder_id: breederMap['Stajnia Toskanska'], father_id: null, mother_id: null },
    { name: 'Hades', breed_code: 'xxoo', birth_date: '2018-07-25', gender: 'ogier', color_id: colorMap['bulany'], breeder_id: breederMap['Hodowla Koni Amerykanskich'], father_id: null, mother_id: null },
    { name: 'Persefona', breed_code: 'xxoo', birth_date: '2018-09-30', gender: 'klacz', color_id: colorMap['gniady'], breeder_id: breederMap['Stajnia Teksanska'], father_id: null, mother_id: null },
    { name: 'Orion', breed_code: 'oo', birth_date: '2020-01-12', gender: 'ogier', color_id: colorMap['kasztanowy'], breeder_id: breederMap['Hodowla Koni Polskich'], father_id: null, mother_id: null },
    { name: 'Andromeda', breed_code: 'oo', birth_date: '2020-03-18', gender: 'klacz', color_id: colorMap['siwy'], breeder_id: breederMap['Stajnia Mazury'], father_id: null, mother_id: null },
    { name: 'Pegasus', breed_code: 'xx', birth_date: '2021-05-22', gender: 'ogier', color_id: colorMap['czarny'], breeder_id: breederMap['Hodowla Koni Niemieckich'], father_id: null, mother_id: null },
    { name: 'Kasjopeja', breed_code: 'xx', birth_date: '2021-07-30', gender: 'klacz', color_id: colorMap['bulany'], breeder_id: breederMap['Stajnia Berlin'], father_id: null, mother_id: null },
    { name: 'Centaur', breed_code: 'xo', birth_date: '2020-09-10', gender: 'ogier', color_id: colorMap['gniady'], breeder_id: breederMap['Hodowla Koni Wloskich'], father_id: null, mother_id: null },
    { name: 'Chiron', breed_code: 'xo', birth_date: '2020-11-15', gender: 'klacz', color_id: colorMap['kasztanowy'], breeder_id: breederMap['Stajnia Toskanska'], father_id: null, mother_id: null },
    { name: 'Atlas', breed_code: 'xxoo', birth_date: '2021-02-20', gender: 'ogier', color_id: colorMap['siwy'], breeder_id: breederMap['Hodowla Koni Amerykanskich'], father_id: null, mother_id: null },
    { name: 'Pleiada', breed_code: 'xxoo', birth_date: '2021-04-25', gender: 'klacz', color_id: colorMap['czarny'], breeder_id: breederMap['Stajnia Teksanska'], father_id: null, mother_id: null },
    { name: 'Sokol', breed_code: 'oo', birth_date: '2019-06-05', gender: 'walach', color_id: colorMap['bulany'], breeder_id: breederMap['Hodowla Koni Francuskich'] },
    { name: 'Jutrzenka', breed_code: 'xx', birth_date: '2020-08-12', gender: 'klacz', color_id: colorMap['gniady'], breeder_id: breederMap['Stajnia Normandska'] },
    { name: 'Blyskawica', breed_code: 'xo', birth_date: '2021-10-20', gender: 'klacz', color_id: colorMap['kasztanowy'], breeder_id: breederMap['Hodowla Koni Polskich'], father_id: null, mother_id: null },
    { name: 'Huragan', breed_code: 'xxoo', birth_date: '2022-01-15', gender: 'ogier', color_id: colorMap['siwy'], breeder_id: breederMap['Stajnia Mazury'], father_id: null, mother_id: null },
    { name: 'Fala', breed_code: 'oo', birth_date: '2021-03-22', gender: 'klacz', color_id: colorMap['czarny'], breeder_id: breederMap['Hodowla Koni Niemieckich'], father_id: null, mother_id: null },
  ];

  // Wstawianie koni z automatycznym obliczaniem rasy na podstawie rodzicow
  const insertedHorses = [];
  const horseNameToIdMap = {};

  const newHorses = [
  { name: 'Meteor', birth_date: '2023-01-10', gender: 'ogier', breed_code: null, color_id: colorMap['gniady'], breeder_id: breederMap['Hodowla Koni Polskich'], father_name: 'Bucefal', mother_name: 'Kleopatra' },
  { name: 'Aurora', birth_date: '2023-02-15', gender: 'klacz', breed_code: null, color_id: colorMap['kasztanowy'], breeder_id: breederMap['Stajnia Mazury'], father_name: 'Thor', mother_name: 'Luna' },
  { name: 'Skylos', birth_date: '2023-03-18', gender: 'ogier', breed_code: null, color_id: colorMap['siwy'], breeder_id: breederMap['Hodowla Koni Niemieckich'], father_name: 'Apollo', mother_name: 'Atena' },
  { name: 'Nyks', birth_date: '2023-04-12', gender: 'klacz', breed_code: null, color_id: colorMap['czarny'], breeder_id: breederMap['Stajnia Berlin'], father_name: 'Apollo', mother_name: 'Atena' },
  { name: 'Tytan', birth_date: '2023-05-05', gender: 'ogier', breed_code: null, color_id: colorMap['bulany'], breeder_id: breederMap['Hodowla Koni Wloskich'], father_name: 'Ares', mother_name: 'Diana' },

  { name: 'Selene', birth_date: '2024-09-12', gender: 'klacz', breed_code: null, color_id: colorMap['gniady'], breeder_id: breederMap['Stajnia Toskanska'], father_name: 'Meteor', mother_name: 'Aurora' },
  { name: 'Orionis', birth_date: '2024-09-13', gender: 'ogier', breed_code: null, color_id: colorMap['kasztanowy'], breeder_id: breederMap['Hodowla Koni Amerykanskich'], father_name: 'Skylos', mother_name: 'Nyks' },
  { name: 'Eos', birth_date: '2024-09-14', gender: 'klacz', breed_code: null, color_id: colorMap['siwy'], breeder_id: breederMap['Stajnia Teksanska'], father_name: 'Tytan', mother_name: 'Selene' },
  { name: 'Zephyros', birth_date: '2024-09-15', gender: 'ogier', breed_code: null, color_id: colorMap['czarny'], breeder_id: breederMap['Hodowla Koni Polskich'], father_name: 'Orionis', mother_name: 'Eos' },
];

  // Najpierw wstawiamy konie bez rodzicow
  for (const horse of horses.filter(h => !h.father_id && !h.mother_id)) {
    const [newRow] = await knex('horses').insert(horse).returning('id');
    const newId = typeof newRow === 'object' ? newRow.id : newRow;
    insertedHorses.push({ ...horse, id: newId });
    horseNameToIdMap[horse.name] = newId;
  }

    // Wstawianie nowej generacji koni
  for (const horse of newHorses) {
    // przypisanie ID rodziców
    horse.father_id = horse.father_name ? horseNameToIdMap[horse.father_name] : null;
    horse.mother_id = horse.mother_name ? horseNameToIdMap[horse.mother_name] : null;

    // automatyczne wyliczanie rasy
    if (horse.father_id && horse.mother_id) {
      const [father, mother] = await Promise.all([
        knex('horses').where({ id: horse.father_id }).select('breed_code').first(),
        knex('horses').where({ id: horse.mother_id }).select('breed_code').first()
      ]);
      const breedCombinations = {
        oo_oo: 'oo',
        oo_xo: 'xo',
        oo_xx: 'xxoo',
        xx_xx: 'xx',
        xx_xo: 'xo',
        xo_xo: 'xo',
        xx_xxoo: 'xxoo'
      };
      horse.breed_code =
        breedCombinations[`${father?.breed_code}_${mother?.breed_code}`] ||
        breedCombinations[`${mother?.breed_code}_${father?.breed_code}`] ||
        horse.breed_code;
    }

    // usuń tymczasowe nazwy rodziców
    delete horse.father_name;
    delete horse.mother_name;

    const [newRow] = await knex('horses').insert(horse).returning('id');
    const newId = typeof newRow === 'object' ? newRow.id : newRow;
    insertedHorses.push({ ...horse, id: newId });
    horseNameToIdMap[horse.name] = newId;

  }

};