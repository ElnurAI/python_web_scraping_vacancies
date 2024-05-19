import psycopg2

class Database():
    def __init__(self):
        self.connection = None
        self.cursor = None

    def run_database(self, all_ads):

        postgres_dic_keys = {'site_name': 'varchar(20)', 'ad_link': 'varchar(200)', 'ad_id': 'integer', 'ad_language': 'varchar(2)',
                             'company_name': 'varchar(100)', 'post_title': 'varchar(100)', 'hr_contact': 'varchar(200)', 'start_date': 'date',
                             'end_date': 'date', 'visitor_number': 'integer', 'city': 'varchar(15)', 'position': 'varchar(100)',
                             'work_experience': 'varchar(20)', 'salary': 'varchar(25)', 'currency': 'varchar(3)', 'job_mode': 'varchar(10)',
                             'work_area': 'varchar(50)', 'category': 'varchar(50)', 'about_job': 'text'}

        try:
            self.connection = psycopg2.connect(host='localhost',
                                               dbname='postgres',
                                               user='postgres',
                                               password='pgElnur356!',
                                               port='5432')
            self.cursor = self.connection.cursor()

            # self.cursor.execute('DROP TABLE IF EXISTS vacancies;')

            # join column names and their types with space & comma
            table_columns_types = ''
            table_columns = ''
            num_of_columns = ''

            for key in postgres_dic_keys.keys():
                str1 = key + ' ' + postgres_dic_keys[key]
                if table_columns_types != '':
                    table_columns_types = table_columns_types + ', ' + str1
                    table_columns = table_columns + ', ' + key
                    num_of_columns = num_of_columns + ', ' + '%s'
                else:
                    table_columns_types = str1
                    table_columns = key
                    num_of_columns = '%s'

            # script to create a vacancies table
            create_table_query = 'CREATE TABLE IF NOT EXISTS vacancies ({0});'.format(table_columns_types)
            self.cursor.execute(create_table_query)

            insert_table_query = 'INSERT INTO vacancies ({0}) VALUES ({1});'.format(table_columns, num_of_columns)

            count_condition_query = '''SELECT COUNT(*)
                                       FROM vacancies 
                                       WHERE ad_id = %s
                                       AND ad_link = %s
                                       AND company_name = %s
                                       AND start_date >= %s 
                                       AND end_date <= %s;'''

            count_inserted_ads = 0
            for ad in all_ads:
                check_values = tuple([ad['ad_id'], ad['ad_link'],  ad['company_name'], ad['start_date'], ad['end_date']])
                self.cursor.execute(count_condition_query, check_values)
                count = self.cursor.fetchall()

                if count[0][0] != 0:
                    continue

                values = tuple(ad.values())
                self.cursor.execute(insert_table_query, values)
                count_inserted_ads += 1

            self.connection.commit()
            print("New " + str(count_inserted_ads) + str(" ads" if count_inserted_ads > 1 else " ad") + " added into database")

        except Exception as error:
            print(error)
        finally:
            if self.cursor is not None:
                self.cursor.close()
            if self.connection is not None:
                self.connection.close()

if __name__ == '__main__':
    pass

