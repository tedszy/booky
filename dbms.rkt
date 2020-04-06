#lang racket

(require db)

(provide (all-defined-out))

(define publication-filename
  (make-parameter "publication.rkt"))

(struct publication (schema rows) #:prefab)

(define (read-publications)
  (call-with-input-file (publication-filename) read))

(define conn (make-parameter #f))

(define (connect)
  (conn (sqlite3-connect #:database 'memory)))

(define (create-publication-table)
  (query-exec (conn)
              "create table publication (
                 uid integer primary key,
                 title text not null,
                 code text not null,
                 block_h integer,
                 block_w integer,
                 cover_h integer,
                 cover_w integer,
                 color text,
                 constraint unique_codes unique(code)
               );"))

(define (drop-publication-table)
  (query-exec (conn) "drop table if exists publication"))

(define (populate-publication-table)
  (call-with-transaction
   (conn)
   (lambda ()
     (for-each
      (lambda (row)
        (match (vector-map false->sql-null row)
          ((vector title code block-h block-w
                   cover-h cover-w color)
           (query-exec
            (conn)
            "insert into publication
               (title,code,block_h,block_w,cover_h,cover_w,color)
             values 
               ($1,$2,$3,$4,$5,$6,$7);"
            title code block-h block-w cover-h cover-w color))))
      (publication-rows (read-publications))))))

(define (fetch-ticket-args-by-code code)
  (query-maybe-row (conn)
                   "select title,cover_h,cover_w,color
                    from publication
                    where code=$1;" code))

(define (fetch-rows-by-title search-string)
  (map (lambda (row)
         (vector-map sql-null->false row))
       (query-rows (conn)
                   "select * from publication
                    where title like $1
                    order by title asc;"
                   (format "~a" search-string))))
